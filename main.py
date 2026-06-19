import sys
from funcionalidades import *

def main():
    if len(sys.argv) < 3:
        print("Escreva a flag de operacao e os argumentos necessarios.")
        return

    flag = sys.argv[1]
    if flag == "-b":
        criarIndice()
    
    elif flag == "-e":
        if len(sys.argv) < 4:
            print("Escreva o arquivo de operacoes.")
            return
        with open(sys.argv[3], 'r') as arq:
            for linha in arq:
                operacao = linha.strip().split()
                if operacao[0] == "b":
                    buscarId()
                elif operacao[0] == "i":
                    inserirJogo()
    
    elif flag == "-p":
        imprimir()
    
    else:
        print("Insira uma flag valida.")
        return

if __name__ == "__main__":
    main()
