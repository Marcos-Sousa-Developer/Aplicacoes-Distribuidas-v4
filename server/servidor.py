from genericpath import isfile
from flask import Flask, request, g, jsonify, make_response, redirect, url_for
from os.path import isfile
from sql import connect_db
import sqlite3, requests, json, webbrowser, ssl
from requests_oauthlib import OAuth2Session

app = Flask(__name__) 

client_id = 'YOUR CLIENT ID HERE'
client_secret = 'YOUR CLIENT SECRET HERE'
redirect_uri= 'YOUR REDIRECT URI'
spotify = OAuth2Session(client_id, redirect_uri=redirect_uri)

@app.before_request #antes de qualquer pedido, conecta a base de dados
def before_request():
    db_is_created = isfile("spotifyBD.db") #se a base de dados já existe
    if db_is_created == False:
        g.connection = connect_db()
    else: 
        g.connection = sqlite3.connect("spotifyBD.db") 
    g.connection.execute("PRAGMA foreign_keys=ON")

#login
@app.route('/login', methods = ["GET"])
def login():
    authorization_base_url = 'https://accounts.spotify.com/authorize'
    authorization_url, state = spotify.authorization_url(authorization_base_url)
    return redirect(authorization_url)

#call back
@app.route('/callback', methods = ["GET"])
def callback():
    token_url = 'https://accounts.spotify.com/api/token'
    spotify.fetch_token(token_url,client_secret=client_secret,authorization_response=request.url)
    return redirect(url_for('.profile'))

#perfil
@app.route("/profile", methods=["GET"])
def profile():
    protected_resource = 'https://api.spotify.com/v1/me'
    return jsonify(spotify.get(protected_resource).json())

#Resquests do tipo utilizador
@app.route('/utilizadores', methods=["GET", "DELETE", "POST", "PUT"]) 
@app.route('/utilizadores/<id>', methods=["GET", "DELETE"])
@app.route('/utilizadores/all/<id>', methods=["GET", "DELETE"]) 
def utilizadores(id = None):

    if request.method == "POST": #CREATE 

        req = request.get_json() #obtém os dados vindos do cliente

        if len(req) == 2: #CREATE UTILIZADOR <nome> <senha> 
            g.connection.execute("INSERT INTO utilizadores (nome, senha) VALUES (?,?)", req)
            response = make_response("Utilizador criado com sucesso", 201)
            response.headers["Content-Type"] = "application/json"
            return response

        else: #<id_user> <id_musica> <avaliacao>
            try:
                cursor = g.connection.execute("SELECT id FROM utilizadores where id=(?)", (req[0],)) #ID user válido?
                id_user = cursor.fetchone()
                cursor = g.connection.execute("SELECT id FROM musicas where id=(?)", (req[1],)) #ID musica válido?
                id_musica = cursor.fetchone()
                cursor = g.connection.execute("SELECT id FROM avaliacoes where sigla=(?)", (req[2],)) #ID avaliação valido?
                id_avaliacao = cursor.fetchone()
                g.connection.execute("INSERT INTO playlists (id_user, id_musica, id_avaliacao) VALUES (?,?,?)", (id_user[0], id_musica[0], id_avaliacao[0])) #insere na base dados
                g.connection.commit()
                response = make_response("Música avaliada com sucesso", 201)
                response.headers["Content-Type"] = "application/json"
                return response

            except sqlite3.IntegrityError:
                response = make_response("O utilizador já avaliou esta música", 400)
                response.headers["Content-Type"] = "application/json"
                return response
            
            except TypeError: # se id_user, id_musica ou id_avaliacao for None
                response = make_response("ID utilizador e/ou ID música não existe, ou o tipo de avaliação não é válida", 400)
                response.headers["Content-Type"] = "application/json"
                return response
    
    elif request.method == "GET": #READ 
        if request.url == "https://localhost:5000/utilizadores": #READ ALL UTILIZADORES
            cursor = g.connection.execute("SELECT id,nome FROM utilizadores")
            dados = cursor.fetchall()
            if len(dados)==0: #se não houver dados
                response = make_response("Não há utilizadores", 400)
                response.headers["Content-Type"] = "application/json"
                return response
            return str(dict(dados))

        elif request.url == "https://localhost:5000/utilizadores/all/" + id: #READ ALL MUSICAS_U <id_user>
            cursor = g.connection.execute("SELECT m.id, m.id_spotify, m.nome FROM musicas AS m, playlists AS p WHERE p.id_user=(?) AND m.id = p.id_musica",(id,))
            dados = cursor.fetchall()
            if len(dados)==0:
                response = make_response("Não foram encontrados dados", 400)
                response.headers["Content-Type"] = "application/json"
                return response
            return str(dados)

        else: #READ UTILIZADOR <id_user>
            try:
                cursor = g.connection.execute("SELECT id, nome FROM utilizadores where id=(?)", (id,)) 
                registo = cursor.fetchone()
                response = make_response("Utilizador: {} com ID: {}".format(registo[1], registo[0]), 200) 
                response.headers["Content-Type"] = "application/json"
                return response

            except TypeError: #Se o registo retornar None
                response = make_response("Não existe um utilizador com este ID", 400)
                response.headers["Content-Type"] = "application/json"
                return response
            
    elif request.method == "DELETE": #DELETE 

        if request.url == "https://localhost:5000/utilizadores": #DELETE ALL UTILIZADORES
            g.connection.execute("DELETE FROM utilizadores")
            response = make_response("Todos os dados dos utilizadores foram apagados", 200)
            response.headers["Content-Type"] = "application/json"
            return response

        elif request.url == "https://localhost:5000/utilizadores/all/" + id: #DELETE ALL MUSICAS_U <id_user>
            cursor = g.connection.execute("SELECT m.id FROM musicas AS m, playlists AS p WHERE p.id_user=(?) AND m.id = p.id_musica", (id,))
            dados = cursor.fetchall()
            if len(dados) == 0:
                response = make_response("Não foram encontrados dados", 400)
                response.headers["Content-Type"] = "application/json"
                return response
            for d in dados:
                cursor = g.connection.execute("DELETE FROM musicas WHERE id=(?)", (d[0],))
            response = make_response("Todas as músicas avaliadas pelo utilizador com o ID {} foram apagadas".format(id), 200)
            response.headers["Content-Type"] = "application/json"
            return response

        else: #DELETE UTILIZADOR <id_user>
            cursor = g.connection.execute("DELETE FROM utilizadores where id=(?)",(id,))
            if cursor.rowcount == 0: #se nenhuma linha foi afetada
                response = make_response("Não existe um utilizador com este ID", 400)
                response.headers["Content-Type"] = "application/json"
                return response
            response = make_response("Utilizador com ID: {}, apagado da Base de dados".format(id), 200)
            response.headers["Content-Type"] = "application/json"
            return response
    
    elif request.method == "PUT": #UPDATE UTILIZADOR <id_user> <password>
        req = request.get_json() #obtém os dados vindos do cliente
        id, senha= req[0],req[1]
        cursor = g.connection.execute("UPDATE utilizadores SET senha=(?) WHERE id=(?)",(senha,id))
        if cursor.rowcount == 0: #se nenhuma linha foi afetada
            response = make_response("Não existe um utilizador com este ID", 400)
            response.headers["Content-Type"] = "application/json"
            return response
        response = make_response("Senha do utilizador atualizada com sucesso", 200)
        response.headers["Content-Type"] = "application/json"
        return response

#Resquests do tipo artista
@app.route('/artistas', methods=["GET","DELETE"])
@app.route('/artistas/<id>', methods=["POST","GET","DELETE"]) 
@app.route('/artistas/all/<id>', methods=["GET","DELETE"]) 
def artistas(id = None):

    if request.method == "POST": #CREATE ARTISTA <id_spotify>
        try:
            r = spotify.get("https://api.spotify.com/v1/artists/"+id)
            data = json.loads(r.content.decode()) #obtém os dados em json e transforma num dicionário
            nome_artista = data["name"]

        except KeyError:  #caso o id seja inválido ou Token expirado
            response = make_response("O ID de artista é inválido ou TOKEN expirado", 400)
            response.headers["Content-Type"] = "application/json"
            return response

        cursor = g.connection.execute("SELECT id_spotify FROM artistas WHERE id_spotify=(?)",(id,))
        if cursor.fetchone() != None: #Caso o artista já esteja na base de dados
            response = make_response("Este artista já se encontra na base de dados", 400)
            response.headers["Content-Type"] = "application/json"
            return response

        g.connection.execute("INSERT INTO artistas (id_spotify,nome) VALUES (?,?)",(id,nome_artista))
        response = make_response("Artista inserido na base de dados", 201)
        response.headers["Content-Type"] = "application/json"
        return response

    elif request.method == "GET": #READ

        if request.url == "https://localhost:5000/artistas": #READ ALL ARTISTAS 
            cursor = g.connection.execute("SELECT * FROM artistas")
            dados = cursor.fetchall()
            if len(dados)==0:
                response = make_response("Não há artistas", 400)
                response.headers["Content-Type"] = "application/json"
                return response
            return str(dados)

        elif request.url == "https://localhost:5000/artistas/all/" + id: #READ ALL MUSICAS_A <id_artista>
            cursor = g.connection.execute("SELECT m.id, m.id_spotify, m.nome FROM musicas AS m, playlists AS p WHERE m.id_artista=(?) AND m.id=p.id_musica", (id,))
            dados = cursor.fetchall()
            if len(dados)==0:
                response = make_response("Não foram encontrados dados", 400)
                response.headers["Content-Type"] = "application/json"
                return response
            return str(dados)

        else: #READ ARTISTA <id_artista>
            try:
                cursor = g.connection.execute("SELECT * FROM artistas WHERE id=(?)", (id,))
                registo = cursor.fetchone()
                id_spotify = registo[1]
                r = spotify.get("https://api.spotify.com/v1/artists/"+id_spotify)
                data = json.loads(r.content.decode())
                if "error" in list(data.keys()): #caso o token esteja expirado
                    response = make_response("TOKEN expirado", 400)
                    response.headers["Content-Type"] = "application/json"
                    return response
            except TypeError: #caso o id não exista
                response = make_response("Não existe um artista com este ID", 400)
                response.headers["Content-Type"] = "application/json"
                return response
            data["id_BaseDados"] = registo[0] #adicionar ao dicionário id da base de dados
            data["id_spotify"] = id_spotify #adicionar ao dicionário id do spotify
            return data
    
    elif request.method == "DELETE": #DELETE 

        if request.url == "https://localhost:5000/artistas": #DELETE ALL ARTISTA
            g.connection.execute("DELETE FROM artistas")
            response = make_response("Todos os dados dos artistas foram apagados", 200)
            response.headers["Content-Type"] = "application/json"
            return response

        elif request.url == "https://localhost:5000/artistas/all/" + id: #DELETE ALL MUSICAS_A <id_artista>
            cursor = g.connection.execute("SELECT m.id FROM musicas AS m, playlists AS p WHERE m.id_artista=(?) AND m.id=p.id_musica",(id,))
            dados = cursor.fetchall()
            if len(dados) == 0:
                response = make_response("Não foram encontrados dados", 400)
                response.headers["Content-Type"] = "application/json"
                return response
            for d in dados:
                cursor = g.connection.execute("DELETE FROM musicas WHERE id=(?)", (d[0],))
            response = make_response("Todas as músicas do artista com o ID {} foram apagadas".format(id), 200)
            response.headers["Content-Type"] = "application/json"
            return response

        else: #DELETE ARTISTA <id_artista>
            cursor = g.connection.execute("DELETE FROM artistas WHERE id=(?)", (id,))
            if cursor.rowcount == 0: #se nenhuma linha foi afetada
                response = make_response("Não existe um artista com este ID", 400)
                response.headers["Content-Type"] = "application/json"
                return response
            response = make_response("Artista com ID: {}, apagado da Base de dados".format(id), 200)
            response.headers["Content-Type"] = "application/json"
            return response

#Resquests do tipo musicas
@app.route('/musicas', methods=["PUT","GET","DELETE"]) 
@app.route('/musicas/<id>', methods=["POST","GET","DELETE"])
@app.route('/musicas/all/<id>', methods=["GET","DELETE"])
def musicas(id = None):

    if request.method == "POST": #CREATE MUSICA <id_spotify>
        try:
            r = spotify.get("https://api.spotify.com/v1/tracks/" + id)
            data = json.loads(r.content.decode()) #obtém os dados em json e transforma num dicionário
            nome_musica = data["name"]
            id_spotify_artista = data["artists"][0]["id"] #obtém o id spotify do artista
        except KeyError:  #caso o id seja inválido ou Token expirado
            response = make_response("O ID da musica é inválido ou TOKEN expirado", 400)
            response.headers["Content-Type"] = "application/json"
            return response 
        
        cursor = g.connection.execute("SELECT id_spotify FROM musicas WHERE id_spotify=(?)",(id,))
        if cursor.fetchone() != None: #Caso a musica já esteja na base de dados
            response = make_response("Esta musica já se encontra na base de dados", 400)
            response.headers["Content-Type"] = "application/json"
            return response

        #caso não exista o artista ao inserir uma música vai adicionar o artista à base de dados
        cursor = g.connection.execute("SELECT id FROM artistas WHERE id_spotify=(?)",(id_spotify_artista,))
        dados_artista = cursor.fetchall()
        if len(dados_artista) == 0: #caso não obtenha nenhuma linha
            r = requests.post('https://localhost:5000/artistas/' + id_spotify_artista, verify='../certs/root.pem',cert=('../certs/cli.crt','../certs/cli.key'))
            cursor = g.connection.execute("SELECT id FROM artistas WHERE id_spotify=(?)",(id_spotify_artista,))
            dados_artista = cursor.fetchall()

        g.connection.execute("INSERT INTO musicas (id_spotify,nome,id_artista) VALUES (?,?,?)",(id,nome_musica,dados_artista[0][0]))
        response = make_response("Música inserida na base de dados", 201)
        response.headers["Content-Type"] = "application/json"
        return response
    
    elif request.method == "GET": #READ

        if request.url == "https://localhost:5000/musicas": #READ ALL MUSICAS
            cursor = g.connection.execute("SELECT * FROM musicas")
            dados = cursor.fetchall()
            if len(dados)==0:
                response = make_response("Não há musicas", 400)
                response.headers["Content-Type"] = "application/json"
                return response
            return str(dados)

        elif request.url == "https://localhost:5000/musicas/all/"+id: #READ ALL MUSICAS <avaliacao>
            cursor = g.connection.execute("SELECT id FROM avaliacoes where sigla=(?)",(id,))
            content_avalicao = cursor.fetchone()
            if content_avalicao == None:
                response = make_response("Tipo de avaliação não é válida", 400)
                response.headers["Content-Type"] = "application/json"
                return response
            cursor = g.connection.execute("SELECT m.id,m.id_spotify,m.nome,m.id_artista FROM musicas AS m, playlists AS p WHERE m.id=p.id_musica AND p.id_avaliacao = (?)",(content_avalicao[0],))
            dados = cursor.fetchall()
            if len(dados)==0:
                response = make_response("Não foram encontrados dados", 400)
                response.headers["Content-Type"] = "application/json"
                return response
            return str(dados) 

        else: #READ MUSICA <id_musica>
            try:
                cursor = g.connection.execute("SELECT * FROM musicas WHERE id=(?)", (id,))
                registo = cursor.fetchone()
                id_spotify = registo[1]
                r = spotify.get("https://api.spotify.com/v1/tracks/" + id_spotify)
                data = json.loads(r.content.decode())
                if "error" in list(data.keys()): #caso o token esteja expirado
                    response = make_response("TOKEN expirado", 400)
                    response.headers["Content-Type"] = "application/json"
                    return response
            except TypeError: #caso o id não exista
                response = make_response("Não existe uma musica com este ID", 400)
                response.headers["Content-Type"] = "application/json"
                return response
            data["id_BaseDados"] = registo[0] #adicionar ao dicionário id da base de dados
            data["id_spotify"] = id_spotify #adicionar ao dicionário id do spotify
            webbrowser.open(data["preview_url"]) #Tocar musica
            return data
    
    elif request.method == "DELETE": #DELETE 

        if request.url == "https://localhost:5000/musicas": #DELETE ALL MUSICAS
            g.connection.execute("DELETE FROM musicas")
            response = make_response("Todos os dados das músicas foram apagados", 200)
            response.headers["Content-Type"] = "application/json"
            return response

        elif request.url == "https://localhost:5000/musicas/all/" + id: #DELETE ALL MUSICAS <avaliacao>
            cursor = g.connection.execute("SELECT id FROM avaliacoes where sigla=(?)", (id,))
            content_avalicao = cursor.fetchone()
            if content_avalicao == None:
                response = make_response("Tipo de avaliação não é válida", 400)
                response.headers["Content-Type"] = "application/json"
                return response

            cursor = g.connection.execute("SELECT m.id FROM musicas AS m, playlists AS p WHERE m.id=p.id_musica AND p.id_avaliacao = (?)", (content_avalicao[0],))
            dados = cursor.fetchall()
            if len(dados)==0:
                response = make_response("Não foram encontrados dados", 400)
                response.headers["Content-Type"] = "application/json"
                return response

            for d in dados:
                cursor = g.connection.execute("DELETE FROM musicas WHERE id=(?)", (d[0],))
            response = make_response("Todas as músicas com avaliação {} foram apagadas".format(id), 200)
            response.headers["Content-Type"] = "application/json"
            return response
            
        else: #DELETE MUSICA <id_musica>
            cursor = g.connection.execute("DELETE FROM musicas WHERE id=(?)", (id,))
            if cursor.rowcount == 0: #se nenhuma linha foi afetada
                response = make_response("Não existe uma musica com este ID", 400)
                response.headers["Content-Type"] = "application/json"
                return response
            response = make_response("Musica com ID: {}, apagada da Base de dados".format(id), 200)
            response.headers["Content-Type"] = "application/json"
            return response
    
    elif request.method == "PUT": #UPDATE MUSICA <id_musica> <avaliacao> <id_user>
        req = request.get_json() #obtém os dados vindos do cliente
        cursor = g.connection.execute("SELECT id FROM utilizadores where id=(?)", (req[2],))
        content_user = cursor.fetchone()
        cursor = g.connection.execute("SELECT id FROM musicas where id=(?)",(req[0],))
        content_musica = cursor.fetchone()
        cursor = g.connection.execute("SELECT id FROM avaliacoes where sigla=(?)",(req[1],))
        content_avalicao = cursor.fetchone()

        if content_user == None:
            response = make_response("ID utilizador não é válido", 400)
            response.headers["Content-Type"] = "application/json"
            return response

        elif content_musica == None:
            response = make_response("ID musica não é válido", 400)
            response.headers["Content-Type"] = "application/json"
            return response

        elif content_avalicao == None:
            response = make_response("Tipo de avaliação não é válida", 400)
            response.headers["Content-Type"] = "application/json"
            return response

        cursor = g.connection.execute("SELECT * FROM playlists where id_user=(?) AND id_musica=(?)",(req[2],req[0]))
        content = cursor.fetchone()
        if content == None:
            response = make_response("Não foi possível atualizar avaliação, a musica não foi avaliada por este utilizador", 400)
            response.headers["Content-Type"] = "application/json"
            return response

        cursor = g.connection.execute("SELECT * FROM playlists WHERE id_user=(?) AND id_musica=(?) AND id_avaliacao=(?)", (content_user[0],content_musica[0],content_avalicao[0]))
        if cursor.fetchone() == None:
            g.connection.execute("UPDATE playlists SET id_avaliacao=(?) WHERE id_user=(?) AND id_musica=(?)", (content_avalicao[0],content_user[0],content_musica[0]))
            response = make_response("Avaliação da música alterada com sucesso", 200)
            response.headers["Content-Type"] = "application/json"
            return response
        response = make_response("Utilizador já fez esta avaliação", 400)
        response.headers["Content-Type"] = "application/json"
        return response

@app.teardown_request #depois de qualquer pedido fecha a base de dados
def teardown_request(error):
    g.connection.commit()
    g.connection.close()
    print()

if __name__ == '__main__':
    context = ssl.SSLContext(protocol=ssl.PROTOCOL_TLS_SERVER)
    context.verify_mode = ssl.CERT_REQUIRED
    context.load_verify_locations(cafile='../certs/root.pem')
    context.load_cert_chain(certfile='../certs/serv.crt',keyfile='../certs/serv.key')
    app.run('localhost', ssl_context=context, debug = True)
