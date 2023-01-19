class VerificaOperacao:
    """Classe verifica operação.
    Verifica se o comando introduzido pelo Cliente é valido retornando True ou False.
    Esta verificação é feita pelo o método operacao(self,metodo), que tem como seus complementares
    os métodos create(self,metodo), read_delete(self,metodo) e update(self,metodo).
    """

    def __create__(self,request): 
        """Verifica um comando com Operação CREATE
        Args:
            request (lista): comando em forma de lista
        Returns:
            boolean: retorna True se operação é válida ou Falso caso inválida
        """

        if request[1] == "UTILIZADOR":
            if len(request) == 4:
                return True 
        
        elif request[1] in ["ARTISTA","MUSICA"]:
            if len(request) == 3:
                return True  
        else: 
            if len(request) == 4:
                return True

        return False  

    def __read_delete__(self,request):
        """Verifica um comando com Operação READ ou DELETE
        Args:
            request (lista): comando em forma de lista
        Returns:
            boolean: retorna True se operação é válida ou Falso caso inválida
        """

        if request[1] in ["UTILIZADOR","ARTISTA","MUSICA"]:
            if len(request) == 3:
                return True 

        elif request[1] == "ALL":
            if len(request) == 3 or len(request) == 4:
                return True

        return False  

    def __update__(self,request):
        """Verifica um comando com  Operação update
        Args:
            request (lista): comando em forma de lista
        Returns:
            boolean: retorna True se operação é válida ou Falso caso inválida
        """

        if request[1] == "MUSICA":
            if len(request) == 5:
                return True 
        
        elif request[1] == "UTILIZADOR":
            if len(request) == 4:
                return True

        return False  

    def operacao(self, comando): 
        """Verifica se uma determinada operação é válida
        Args:
            comando (list): comando em forma de lista
        Returns:
            booelan: retorna True se operação é válida ou Falso caso inválida
        """
        req = comando.split() #coverte o comando numa lista
        operacao = req[0] #obter a operação

        if operacao == "CREATE":
            return self.__create__(req)

        elif operacao in ["READ","DELETE"]:
            return self.__read_delete__(req)
        
        elif operacao == "UPDATE":
            return self.__update__(req) 
                
        return False
    
    def __repr__(self): 
        print("Operações permitidas: ")
        print()
        print("Operação CREATE + <parâmetro>")
        print("+ UTILIZADOR <nome> <senha> ou")
        print("+ ARTISTA <id_spotify> ou") 
        print("+ MUSICA <id_spotify> ou")
        print("+ <id_user> <id_musica> <avaliacao>.")
        print()
        print("Operação READ/DELETE + <parâmetro>")
        print("+ UTILIZADOR <id_user> ou")
        print("+ ARTISTA <id_artista> ou")
        print("+ MUSICA <id_musica> ou")
        print("+ ALL < UTILIZADORES | ARTISTAS | MUSICAS> ou")
        print("+ ALL MUSICAS_A <id_artista> ou")
        print("+ ALL MUSICAS_U <id_user> ou")
        print("+ ALL MUSICAS <avaliacao>.")
        print()
        print("Operação UPDATE + <parâmetro>")
        print("+ MUSICA <id_musica> <avaliacao> <id_user> ou")
        print("+ UTILIZADOR <id_user> <password>.")
        print()
        print("Para sair, executar EXIT ou Ctrl+C.") 
        return ""