<p align="center">
    <img src="https://www.freepnglogos.com/uploads/server-png/server-icon-download-icons-17.png" alt="Logo" width="80" height="80">
</p>

# <h1 align="center">Serviço Web para gerir um sistema simplificado de classificação de músicas de utilizadores</h1>
<h4 align="center">Projeto para a cadeira de Aplicações Distribuídas (Parte4) (2021/2022)</h4>

<hr>

# Objetivo
No <a href="https://github.com/Marcos-Sousa-Developer/Aplicacoes_Distribuidas_v3">Projeto3</a> foi concretizado um serviço WEB para gerir um sistema simplificado de classificação de músicas de utilizadores. Para esse efeito, foram utilizados no servidor a framework de desenvolvimento WEB Flask e o motor de base de dados SQL sqlite. O programa cliente utiliza o módulo requests para implementar a interação cliente/servidor baseada no HTTP. <br>
Esta última parte incide sobre medidas de segurança para o projeto anterior

<hr> 

# Notas 

## Autenticação e confidencialidade da comunicação 

O protocolo SSL/TLS v1.3 deverá ser utilizado com o Flask e com o módulo requests (ver os parâmetros cert e verify) para que o cliente e o servidor verifiquem mutuamente a autenticidade do interlocutor e para que a comunicação seja confidencial (cifrada). Para este
efeito, o cliente e o servidor deverão ter certificados de chave pública assinados por uma Certificate Authority (CA). Ou seja, os certificados não devem ser auto-assinados.
A implementação no Flask será feita através da classe SSLContext do módulo ssl da biblioteca padrão do Python. 

## Autorização 

O protocolo OAuth2 deverá ser utilizado com o Flask e com o módulo requests_oauthlib para que a aplicação possa pedir autorização para usar os recursos
disponiblizados pelo servidor de recursos do Spotify. Para este efeito, o URI de callback do servidor deverá estar registado na API de OAuth do Spotify de forma que o mesmo possa ser receber o código de autorização para pedir tokens de acesso. <br>
A aplicação Flask deverá incluir três novos recursos (/login, /callback e /profile, para que o utilizador possa dar autorização através do navegador à aplicação para aceder a recursos protegidos antes de iniciar a interação com os outros recursos implementados no Projeto 3. <br>
O recurso protegido que será acedido pelo recurso /profile será o perfil do utilizador no Spotify (i.e., https://api.spotify.com/v1/me). 

# Passos

## 1ºPasso: Autenticação 

### Para ter acesso à API REST do Spotify é preciso seguir alguns passos de autenticação e autorização

1. Entrar em https://developer.spotify.com/dashboard/
2. Fazer o login ou criar uma nova conta.
3. Registar uma applicação. Para isso basta definir o nome da aplicação e descrever
brevemente o objetivo da aplicação.
4. Copiar o Client ID e o Client Secret
5. Ler atentamente a documentação da API Web do Spotify.
6. Executar alguns testes simples na Spotify Web API Console.
7. Após preencher os campos do pedido, é preciso gerar um token OAuth para estar
autorizado a executar o comando.
8. Executar alguns testes simples com o comando curl, como no exemplo a seguir.
Pode-se substituir o campo nome_artista pelo nome do artista que pretende buscar na
plataforma, assim como deve-se substituir o campo meu_OAuthToken pelo token
obtido no passo anterior: 

```bash
curl -X "GET"
"https://api.spotify.com/v1/search?q=nome_artista&type=artist" -H
"Accept: application/json" -H "Content-Type: application/json" -H
"Authorization: Bearer meu_OAuthToken" 
``

## 2ºPasso: Conexão

#### **Run these two on different terminals** 

```bash
python3 client/cliente.py 
```
```bash
python3 python3 server/servidor.py
```
<hr> 

# Instruções (In the client.py terminal)

## Comando CREATE

```bash
CREATE UTILIZADOR <nome> <senha> 
```
```bash
CREATE ARTISTA <id_spotify> 
```
```bash
CREATE MUSICA <id_spotify> 
```
```bash
CREATE <id_user> <id_musica> <avaliacao>
```

## Comando READ ou DELETE

```bash
READ|DELETE UTILIZADOR <id_user>
```
```bash
READ|DELETE ARTISTA <id_artista>
```
```bash
READ|DELETE MUSICA <id_musica>
```
```bash
READ|DELETE ALL < UTILIZADORES | ARTISTAS | MUSICAS>
```
```bash
READ|DELETE ALL MUSICAS_A <id_artista>
```
```bash
READ|DELETE ALL MUSICAS_U <id_user>
```
```bash
READ|DELETE ALL MUSICAS <avaliacao>
```

## Comando UPDATE

```bash
UPDATE MUSICA <id_musica> <avaliacao> <id_user>
```
```bash
UPDATE UTILIZADOR <id_user> <password>
```

