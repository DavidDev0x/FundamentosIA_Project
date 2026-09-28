import heapq
import math

MOVIMENTOS = (
    (0, 1, 1.0), (0, -1, 1.0), (1, 0, 1.0), (-1, 0, 1.0),
    (1, 1, math.sqrt(2)), (1, -1, math.sqrt(2)),
    (-1, 1, math.sqrt(2)), (-1, -1, math.sqrt(2)),
)

def heuristica(a, b):
    return math.hypot(b[0] - a[0], b[1] - a[1])

def a_estrela(custo_social, bloqueados, inicio, objetivo):
    linhas, colunas = custo_social.shape
    if bloqueados[inicio] or bloqueados[objetivo]:
        raise ValueError("Inicio ou objetivo esta bloqueado.")

    abertos = [(heuristica(inicio, objetivo), inicio)]
    veio_de = {}
    g = {inicio: 0.0}
    fechados = set()

    while abertos:
        _, atual = heapq.heappop(abertos)
        if atual in fechados:
            continue
        if atual == objetivo:
            caminho = [atual]
            while atual in veio_de:
                atual = veio_de[atual]
                caminho.append(atual)
            return caminho[::-1]

        fechados.add(atual)
        for dl, dc, custo_movimento in MOVIMENTOS:
            vizinho = (atual[0] + dl, atual[1] + dc)
            if not (0 <= vizinho[0] < linhas and 0 <= vizinho[1] < colunas):
                continue
            if bloqueados[vizinho]:
                continue

            novo_g = g[atual] + custo_movimento + float(custo_social[vizinho])
            if novo_g < g.get(vizinho, float("inf")):
                veio_de[vizinho] = atual
                g[vizinho] = novo_g
                heapq.heappush(
                    abertos,
                    (novo_g + heuristica(vizinho, objetivo), vizinho),
                )
    return None
