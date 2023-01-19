import sqlite3

def connect_db():
    """Criar uma base dados de nome spotifyBD.bd 
       e consequentemente executar as query's

       args: query (query sql a ser executada)

       return conexão e o cursor
    """
    
    query_create_tables = """CREATE TABLE utilizadores (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT,senha TEXT);
    CREATE TABLE musicas (id INTEGER PRIMARY KEY AUTOINCREMENT, id_spotify TEXT,nome TEXT,id_artista INTEGER,FOREIGN KEY(id_artista) REFERENCES artistas(id) ON DELETE CASCADE);
    CREATE TABLE artistas (id INTEGER PRIMARY KEY AUTOINCREMENT,id_spotify TEXT,nome TEXT);
    CREATE TABLE avaliacoes (id INTEGER PRIMARY KEY,sigla TEXT,designacao TEXT);
    CREATE TABLE playlists (id_user INTEGER,id_musica INTEGER,id_avaliacao INTEGER,PRIMARY KEY (id_user, id_musica),FOREIGN KEY(id_user) REFERENCES utilizadores(id) ON DELETE CASCADE,FOREIGN KEY(id_musica) REFERENCES musicas(id) ON DELETE CASCADE,FOREIGN KEY(id_avaliacao) REFERENCES avaliacoes(id) ON DELETE CASCADE);
    """

    query_insert = """INSERT INTO avaliacoes (id, sigla, designacao) VALUES (?,?,?)"""

    avaliacoes = [(1, "M", "Medíocre"),(2, "m", "Mau"),(3, "S", "Suficiente"),(4, "B", "Boa"),(5, "MB", "Muito Boa")]

    sql_query = query_create_tables.splitlines() #lista de querys

    connection = sqlite3.connect("spotifyBD.db") #conectar a base de dados de nome "spotifyBD.db"
    cursor = connection.cursor() 

    for query in sql_query:

        cursor.execute(query)
        connection.commit()

    cursor.executemany(query_insert,avaliacoes) #para a query executa cada avaliação
    connection.commit() 

    return connection