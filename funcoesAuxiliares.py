import sys
from struct import pack, unpack
from constantes import ORDEM, TAM_CAB, TAM_PAG, CAMINHO_BTREE

arquivoArvores = CAMINHO_BTREE

class Pagina:
    def __init__(self):
        self.numChaves = 0
        self.chaves = [-1] * (ORDEM - 1)
        self.offsets = [-1] * (ORDEM - 1) 
        self.filhos = [-1] * ORDEM

    #monta o formato do struct: numChaves + chaves + offsets + filhos, tudo "i" (4 bytes com sinal)
    def __formato_struct(self):
        qtd_campos = 1 + (ORDEM - 1) + (ORDEM - 1) + ORDEM
        return f"<{qtd_campos}i"

    #serializa a pagina pra bytes, no tamanho fixo TAM_PAG, pra escrever no arquivo
    def to_bytes(self):
        return pack(
            self.__formato_struct(),
            self.numChaves,
            *self.chaves,
            *self.offsets,
            *self.filhos,
        )

    #desserializa os bytes lidos do arquivo de volta pra um objeto Pagina
    @staticmethod
    def from_bytes(dados_bytes):
        pag = Pagina()
        valores = unpack(pag.__formato_struct(), dados_bytes)

        pag.numChaves = valores[0]
        i = 1
        pag.chaves = list(valores[i : i + (ORDEM - 1)])
        i += ORDEM - 1
        pag.offsets = list(valores[i : i + (ORDEM - 1)])
        i += ORDEM - 1
        pag.filhos = list(valores[i : i + ORDEM])

        return pag


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

def insereChave(chave, offset, rrnAtual):
    if rrnAtual == -1:
        #caso base: no folha acessnado um no que nao existe
        #dai vai retornar a chave, o offset e true que vai promover
        return chave, offset, -1, True
    else:
        #le a pagina
        pag = lerPagina(rrnAtual)
        #busca a posicao aonde a chave devia estar na pag 
        achou, pos = buscaNaPagina(chave, pag)
        
    if achou:
        return "Erro: chave duplicada"

    #recursao pra descer ate o filho certo
    desce = insereChave(chave, offset, pag.filhos[pos])
    if desce == "Erro: chave duplicada":
        return desce
    #adiciona as info nas variaveis pra inserir depois a chave promovida
    chavePro, offsetPro, filhoDpro, promo = desce

    #se nao promoveu(já inseriu em baixo) retorna nada
    if not promo:
        return -1, -1, -1, False
    else:
        #se tiver espaco na pagina (por isso o ORDEM -1)
        if pag.numChaves < (ORDEM - 1):
            #coloca a chave promovida na pagina
            insereChavePromo(chavePro, offsetPro, filhoDpro, pag)
            #escreve no arquivo
            escrevePagina(rrnAtual, pag)
            #e devolve que nao vai ter mais promocao
            return -1, -1, -1, False
        else:
            #dai se tiver cheia divide a pagina e pega a do meio pra promover
            chavePro, offsetPro, filhoDpro, pag, novaPag = dividePagina(chavePro, offsetPro, filhoDpro, pag)
            #metade esquerda
            escrevePagina(rrnAtual, pag)
            #metae direita com o rrn novo
            escrevePagina(filhoDpro, novaPag)
            #e devolve a chave promovida e o rrn do filho direito
            return chavePro, offsetPro, filhoDpro, True

def lerPagina(rrn):
    offset = rrn * TAM_PAG + TAM_CAB
    with open(arquivoArvores, 'rb') as arq:
        arq.seek(offset)
        #le os bytes da pagina
        pag_bytes = arq.read(TAM_PAG)
        #desserializa os bytes pro objeto Pagina e devolve
        return Pagina.from_bytes(pag_bytes)

def escrevePagina(rrn, pag):
    offset = rrn * TAM_PAG + TAM_CAB
    with open(arquivoArvores, 'r+b') as arq:
        arq.seek(offset)  # vai para a posicao da pagina
        arq.write(pag.to_bytes())  # serializa e escreve os bytes da pagina

def insereChavePromo(chave, offset, filhoD, pag):
    #se a pagina tiver cheia, coloca mais um espaco pra chave e pro filho
    if pag.numChaves == (ORDEM - 1):
        pag.chaves.append(-1)
        pag.offsets.append(-1)
        pag.filhos.append(-1)
    
    i = pag.numChaves
    #vai movendo as chaves e os filhos pra direita ate achar a posicao certa
    while i > 0 and chave < pag.chaves[i - 1]:
        #move as chaves, os offsets e os filhos uma pra direita
        pag.chaves[i] = pag.chaves[i - 1]
        pag.filhos[i + 1] = pag.filhos[i]
        pag.offsets[i] = pag.offsets[i-1]
        i -= 1
    #escreve na posicao livre
    pag.chaves[i] = chave
    pag.offsets[i] = offset
    #pega o * do filho da direita que subiu tambem
    pag.filhos[i + 1] = filhoD
    #aumenta num de chaves
    pag.numChaves += 1

def dividePagina(chave, offset, filhoD, pag):
    #coloca a chave promovida na pagina cheia
    insereChavePromo(chave, offset, filhoD, pag)
    meio = ORDEM // 2

    #promove a chave do meio da pagina
    chavePro = pag.chaves[meio]
    offsetPro = pag.offsets[meio]
    #pega o rrn novo da pagina que vai ser criada
    filhoDpro = novoRRN()

    #cria uma nova pagina e coloca metade das chaves nela
    pAtual = Pagina() 
    pAtual.numChaves = meio
    for i in range(meio):
        pAtual.chaves[i] = pag.chaves[i]
        pAtual.offsets[i] = pag.offsets[i]
        pAtual.filhos[i] = pag.filhos[i]
    pAtual.filhos[meio] = pag.filhos[meio] #dai o meio dos filhos da pAtual vai ser o filho da direita da ultima chave da primeira metade da pag

    #outra pagina com a outra metade tirando 1(o do meio que subiu)
    pNova = Pagina()
    pNova.numChaves = pag.numChaves - meio - 1
    for i in range(pNova.numChaves):
        pNova.chaves[i] = pag.chaves[meio + 1 + i]
        pNova.offsets[i] = pag.offsets[meio + 1 + i]
        pNova.filhos[i] = pag.filhos[meio + 1 + i]
    pNova.filhos[pNova.numChaves] = pag.filhos[pag.numChaves]

    #returna a chave que subiu e as duas metades
    return chavePro, offsetPro, filhoDpro, pAtual, pNova

def novoRRN():
    with open(arquivoArvores, 'ab') as arq:
        #pega o final do arquivo e o offset atual que é o tamanho do arquivo
        arq.seek(0, 2)
        offset = arq.tell()
        return (offset - TAM_CAB) // TAM_PAG

def insereNaArvore(chave, offset, rrnRaiz):
    #chama a recursao com a raiz pra ver se ta inserindo chave que ja existe
    desce = insereChave(chave, offset, rrnRaiz)
    if desce == "Erro: chave duplicada":
        return rrnRaiz, False
    
    chavePro, offsetPro,filhoDpro, promo = desce

    if promo:
        pNova = Pagina()
        #a chave promovida vai pras chaves da raiz nova
        pNova.chaves[0] = chavePro
        pNova.offsets[0] = offsetPro
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
        return rrnNovaRaiz, True

    return rrnRaiz, True