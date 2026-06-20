#caminhos dos arquivos usados pelo trabalho
CAMINHO_JOGOS = "games.dat"
CAMINHO_BTREE = "btree.dat"

#ordem da arvore-B, trocar aqui pra testar ordens diferentes
ORDEM = 5

#tamanho em bytes de cada campo inteiro (chave, offset, filho, numChaves)
#usando inteiro com sinal de 4 bytes pra caber o -1 de "vazio"
TAM_INT = 4

#cabecalho do arquivo btree.dat: so guarda o RRN da raiz
TAM_CAB = TAM_INT

#tamanho de uma pagina = numChaves + (ORDEM-1) chaves + (ORDEM-1) offsets + ORDEM filhos
TAM_PAG = TAM_INT * (1 + 2 * (ORDEM - 1) + ORDEM)