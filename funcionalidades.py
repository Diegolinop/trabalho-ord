import sys
from funcoesAuxiliares import *
from constantes import *

#-b
def criarIndice():
    try:
        #se o CAMINHO_JOGOS nao existir ele ja vai pro erro
        with open(CAMINHO_JOGOS, 'rb') as arqJogos:
            raiz = -1
            with open(CAMINHO_BTREE, 'wb') as arqArvb:
                #signed= True pra usar o -1, fiz primeiro sem e deu erro
                arqArvb.write(raiz.to_bytes(TAM_CAB, byteorder= 'little', signed=True))
    
            final = False
            while not final:
                offset = arqJogos.tell() #pega o offset pra salvar na arvore
                tam_bytes = arqJogos.read(2) #le o tamanho do arq
                if not tam_bytes:
                    final = True
                    continue

                tam = int.from_bytes(tam_bytes, byteorder='little')
                linha_bytes = arqJogos.read(tam)
                linha = linha_bytes.decode('utf-8')
                chave = int(linha.split('|')[0])

                #insere a chave e se mudar a raiz, troca pela nova
                raiz, nada = insereNaArvore(chave, offset, raiz)
    
        with open(CAMINHO_BTREE, 'r+b') as arqArvb:
            arqArvb.seek(0)
            #pra escrever o rrn da raiz no cabecalho
            arqArvb.write(raiz.to_bytes(TAM_CAB, byteorder= 'little', signed= True))

        print("Operação concluída com sucesso!\n")
        return
    
    except FileNotFoundError:
        print(f'Erro: Arquivo "{CAMINHO_JOGOS}" nao foi encontrado\n')
        return

#-e (BUSCA)
def buscarId(chave_buscada):
    print(f'Busca pelo registro de chave "{chave_buscada}"')
    chave = int(chave_buscada)

    try:
        with open(CAMINHO_BTREE, 'rb') as arqArvb:
            #pega o tamanho da raiz
            raiz_bytes = arqArvb.read(TAM_CAB)
            raiz = int.from_bytes(raiz_bytes, byteorder= 'little', signed=True)
        
        #procura na arvore e pega o rrn e a posicao
        achou, rrn, pos = buscaNaArvore(chave,raiz)
        if achou:
            #pega a pagina do rrn e o offset da mesma posicao da chave
            pag = lerPagina(rrn)
            offset = pag.offsets[pos]

            with open(CAMINHO_JOGOS, 'rb') as arqJogos:
                arqJogos.seek(offset)
                #pega o tamanho da string do jogo
                tam_bytes = arqJogos.read(2)
                tam = int.from_bytes(tam_bytes, byteorder='little')
                registro = arqJogos.read(tam).decode('utf-8')
                print(f'{registro} ({tam} bytes - offset {offset})\n')
        else:
            print(f'Erro: chave "{chave_buscada}" não encontrada\n')
    except FileNotFoundError:
        print("Erro: Arquivos de dados ou arquivo de indice nao encontrados\n")
        sys.exit()

    return

#-e (INSERCAO)
def inserirJogo(arg):
    chave = int(arg.split('|')[0])
    print(f'Inserção do registro de chave "{chave}"')

    with open(CAMINHO_BTREE, 'rb') as arqArvb:
        raiz = int.from_bytes(arqArvb.read(TAM_CAB), byteorder='little', signed=True)

    achou, rrn, pos = buscaNaArvore(chave, raiz)
    if achou:
        print(f'Erro: chave "{chave}" duplicada\n')
        return

    registro = arg.encode('utf-8')
    tam = len(registro)
    with open(CAMINHO_JOGOS, 'ab') as arqJogos:
        offset = arqJogos.tell()
        arqJogos.write(tam.to_bytes(2, byteorder='little'))
        arqJogos.write(registro)

    raiz, _ = insereNaArvore(chave, offset, raiz)
    with open(CAMINHO_BTREE, 'r+b') as arqArvb:
        arqArvb.seek(0)
        arqArvb.write(raiz.to_bytes(TAM_CAB, byteorder='little', signed=True))

    print(f'{arg} ({tam} bytes - offset {offset})\n')

#-p (IMPRIMIR)
def imprimir():
    try:
        with open(CAMINHO_BTREE, 'rb') as arqArvb:
            raiz = int.from_bytes(arqArvb.read(TAM_CAB), byteorder='little', signed=True)
            arqArvb.seek(0, 2)
            tamArq = arqArvb.tell()
    except FileNotFoundError:
        print(f'Erro: Arquivo "{CAMINHO_BTREE}" nao encontrado\n')
        return

    numPaginas = (tamArq - TAM_CAB) // TAM_PAG

    for rrn in range(numPaginas):
        pag = lerPagina(rrn)
        ehRaiz = (rrn == raiz)

        if ehRaiz:
            print('\n' + '- ' * 10 + 'Raiz' + ' -' * 10)

        print(f'Página {rrn}:')
        print('Chaves = ' + ' | '.join(str(c) for c in pag.chaves))
        print('Offsets = ' + ' | '.join(str(o) for o in pag.offsets))
        print('Filhos = ' + ' | '.join(str(f) for f in pag.filhos))

        if ehRaiz:
            print('- ' * 17)
        print()