import sys
from funcionalidades import *

def main():
    if len(sys.argv) < 2:
        print("Escreva a flag de operacao e os argumentos necessarios.")
        return

    flag = sys.argv[1]
    if flag == "-b":
        criarIndice()
    
    elif flag == "-e":
        if len(sys.argv) < 3:
            print("Escreva o arquivo de operacoes.")
            return
        nome_arquivo = sys.argv[2]
        try:
            with open(sys.argv[2], 'r') as arq:
                for linha in arq:
                    linha = linha.strip()
                    #coloquei o maxsplit = 1 pra separar no comando e no resto da linha
                    operacao = linha.split(maxsplit = 1) 
                    if operacao[0] == "b":
                        buscarId(operacao[1])
                    elif operacao[0] == "i":
                        inserirJogo(operacao[1])
            print(f'As operações do arquivo "{nome_arquivo}" foram executadas com sucesso!')
        except FileNotFoundError:
            print(f'Erro: Arquivo "{sys.argv[2]}" nao encontrado')
            
    elif flag == "-p":
        imprimir()
    
    else:
        print("Insira uma flag valida.")
        return

if __name__ == "__main__":
    main()
