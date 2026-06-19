import sys
from struct import pack, unpack

#variaveis globais
ORDEM = 5
TAM_CAB = 4
TAM_PAG = 128
arquivoArvores = 'arvore.bin'


#outras funcoes pra usar essas auxiliares

def novoRRN():
    with open(arquivoArvores, 'ab') as arq:
        arq.seek(0, 2)  #fim do arq
        offset = arq.tell()  #tamanho do arq
        return (offset - TAM_CAB) // TAM_PAG  #rrn da nova pagina

class Pagina:
    def __init__(self):
        self.numChaves = 0
        self.chaves = [-1] * (ORDEM - 1)
        self.offsets = [-1] * (ORDEM - 1) 
        self.filhos = [-1] * ORDEM


def buscaNaArvore(chave, rrn):
    if rrn == -1:
        #nao achou, sem rrn e posicao nula
        return False, -1, -1
    else:
        pag = lerPagina(rrn)
        #coloca na "pos" a posicao da "chave" em "pag" ou aque deveria estar se nao tiver
        achou, pos = buscaNaPagina(chave, pag)

        #achou, devolve o rrn e a posicao
        if achou:
            return True, rrn, pos
        else:
            #se nao achou busca dnv na pagina filha
            return buscaNaArvore(chave, pag.filhos[pos])

def buscaNaPagina(chave, pag):
    #comeca na posicao 0
    pos = 0
    #continua procurando enquanto a chave for maior que a da posicao atual
    #ou nao tiver chegado no final da pagina
    while pos < pag.numChaves and chave > pag.chaves[pos]:
        pos += 1
    if pos < pag.numChaves and chave == pag.chaves[pos]:
        #achou, devolve a posicao
        return True, pos
    else: 
        #nao achou, devole a posicao aonde devia estar
        return False, pos

def insereChave(chave, rrnAtual):
    if rrnAtual == -1:
        #pega a chave que vai ser promovida
        chavePro = chave
        #rrn do filho direito da chave promovida que nao existe ainda
        filhoDpro = -1
        #devolve a confirmacao da promocao
        return chavePro, filhoDpro, True
    else:
        #le a pagina
        pag = lerPagina(rrnAtual)
        #busca a posicao aonde a chave devia estar na pag 
        achou, pos = buscaNaPagina(chave, pag)
        
    if achou:
        return "Erro: chave duplicada"
    #insere dai na pagina filha aonde a chave devia estar
    chavePro, filhoDpro, promo = insereChave(chave, pag.filhos[pos])

    #se nao promoveu retorna nada
    if not promo:
        return -1, -1, False
    else:
        #se tiver espaco na pagina (por isso o ORDEM -1)
        if pag.numChaves < (ORDEM - 1):
            #coloca a chave promovida na pagina
            insereNaPagina(pag, chavePro, filhoDpro)
            #escreve no arquivo
            escrevePagina(rrnAtual, pag)
            #e devolve que nao teve promocao
            return -1, -1, False
        else:
            #dai se tiver cheia divide a pagina e pega a do meio pra promover
            chavePro, filhoDpro, pag, novaPag = dividePagina(chavePro, filhoDpro, pag)
            escrevePagina(rrnAtual, pag)
            #escreve a pag nova no arquivo com o rrn novo
            escrevePagina(filhoDpro, novaPag)
            #e devolve a chave promovida e o rrn do filho direito
            return chavePro, filhoDpro, True

def lerPagina(rrn):
    offset = rrn * TAM_PAG + TAM_CAB
    with open(arquivoArvores, 'rb') as arq:
        arq.seek(offset)
        #le os bytes da pagina
        pag_bytes = arq.read(TAM_PAG)
        #devolve os bytes lidos
        return pag_bytes

def escrevePagina(rrn, pag_bytes):
    offset = rrn * TAM_PAG + TAM_CAB
    with open(arquivoArvores, 'r+b') as arq:
        arq.seek(offset)  # vai para a posicao da pagina
        arq.write(pag_bytes)  # escreve os bytes da pagina

def insereChavePromo(chave, filhoD, pag):
    #se a pagina tiver cheia, coloca mais um espaco pra chave e pro filho
    if pag.numChaves == (ORDEM - 1):
        pag.chaves.append(-1)
        pag.filhos.append(-1)
    
    i = pag.numChaves
    #vai movendo as chaves e os filhos pra direita ate achar a posicao certa
    while i > 0 and chave < pag.chaves[i - 1]:
        #move a chave uma pra direita
        pag.chaves[i] = pag.chaves[i - 1]
        #move o filho uma pra direita
        pag.filhos[i + 1] = pag.filhos[i]
        i -= 1
    pag.chaves[i] = chave
    pag.filhos[i + 1] = filhoD
    pag.numChaves += 1

def dividePagina(chave, filhoD, pag):
    #coloca a chave promovida na pagina cheia
    pag = insereChavePromo(chave, filhoD, pag)
    meio = ORDEM // 2
    #promove a chave do meio da pagina
    chavePro = pag.chaves[meio]
    #pega o rrn novo da pagina que vai ser criada
    filhoDpro = novoRRN()
    #a pagina atual pega do comeco ate o meio e a nova do meio ate ofinal   
    pAtual = pag[:meio]
    pNova = pag[meio + 1:]
    return chavePro, filhoDpro, pAtual, pNova

def novoRRN():
    with open(arquivoArvores, 'ab') as arq:
        #pega o final do arquivo e o offset atual que é o tamanho do arquivo
        arq.seek(0, 2)
        offset = arq.tell()
        return (offset - TAM_CAB) // TAM_PAG

def insereNaArvore(chave, rrnRaiz):
    #coloca a chave na rai e ve se promoveu ou nao
    chavePro, filhoDpro, promo = insereChave(chave, rrnRaiz)
    #se promoveu cria uma nova raiz
    if promo:
        pNova = Pagina()
        #a chave promovida vai pras chaves da raiz nova
        pNova.chaves[0] = chavePro
        #a raiz antiga vira o filho esquerdo da raiz nova
        pNova.filhos[0] = rrnRaiz
        #e o filho direito da chave promovida vira o filho direito 
        pNova.filhos[1] = filhoDpro
        #incrementa o numero de chaves da nova raiz
        pNova.numChaves += 1
        #pega o rrn da nova raiz
        rrnNovaRaiz = novoRRN()
        #escreve a nova raiz no arquivo
        escrevePagina(rrnNovaRaiz, pNova)
        return rrnNovaRaiz

    return rrnRaiz

def principal():
    try:
        with open(arquivoArvores, 'r+b') as arqArvb:
            #le o cabecalho que é o rrn da raiz
            raiz_bytes = arqArvb.read(TAM_CAB)
            #transforma os bytes em inteiro
            raiz = int.from_bytes(raiz_bytes, byteorder='big')
    except:
        with open(arquivoArvores, 'wb') as arqArvb:
            raiz = 0
            raiz_bytes = raiz.to_bytes(TAM_CAB, byteorder='big')
            #escreve a raiz no cabecalho 
            arqArvb.write(raiz_bytes)
            #cria a pag da raiz vazia
            pag = Pagina()
            #escreve a pagina vazia no arquivo
            arqArvb.write(pag.to_bytes())
    
    #abre o arquivo pra inserir as chaves
    with open(arquivoArvores, 'r+b') as arqArvb:
        for chave in chaves:
            #insere a chave na arvore e se tiver promocao cria nova raiz
            #dai tem que atualizar o rrn no cabecalho
            raiz = insereNaArvore(chave, raiz)
        arqArvb.seek(0)
        #escreve o RRN da raiz no cabecalho
        arqArvb.write(raiz.to_bytes(TAM_CAB, byteorder='big'))        
