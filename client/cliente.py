from verifica import VerificaOperacao
from encaminhador import Encaminhador
import sys,requests

vp = VerificaOperacao() #classe verifica operacoes
print(vp)
enc = Encaminhador() #classe a caminha request

while True:

    try:
        comando = input("comando > ") # Inserir comando

        if comando == "EXIT": #para sair da função
            print("Vou encerrar")
            sys.exit(0)

        elif len(comando.split()) == 0: #caso não sejam inseridos dados  
            print("Tem de inserir dados")
            print()

        elif len(comando.split()) > 2: #Todas as operacoes tem mais de que 2 argumentos

            if vp.operacao(comando) == True: #caso o comando seja válido
                resposta = enc.encaminha(comando) #faz pedido ao servidor/app

                if resposta == None:
                    print("Operação inválida")
                else:
                    print("Status: ",resposta.status_code)
                    print(resposta.content.decode()) #imprime o conteudo da resposta
                    print("Headers: ",resposta.headers)
                    print()
            else:
                print("Operação inválida")
                print()
        else: 
            print("Operação inválida")
            print()
    
    except KeyboardInterrupt: 
        print()
        print("Ctrl+C ativado, vou encerrar")
        sys.exit(0)
    
    except requests.exceptions.ConnectionError:
        print()
        print("O Servidor/App está desconectado, certifique-se que está ligado")
        print()