import os

import matplotlib.pyplot as plt
import numpy as np

from agente import Agente
from algoritmo import a_estrela

LINHAS = COLUNAS = 30
INICIO = (1, 15)
OBJETIVO = (28, 15)

# Aproximação usada no protótipo:
# 2 células da grade representam aproximadamente 1 metro.
CELULAS_POR_METRO = 2

# Limites laterais aproximados do corredor.
# O algoritmo não interpreta a fotografia; por isso a geometria precisa
# ser representada explicitamente na grade.
LIMITE_ESQUERDO = {
    y: max(0, int(round(5.5 - 0.12 * y)))
    for y in range(LINHAS)
}
LIMITE_DIREITO = {
    y: min(COLUNAS - 1, int(round(28.5 - 0.03 * y)))
    for y in range(LINHAS)
}

# Móvel/ilha central observado nos frames.
# Formato: (x_min, x_max, y_min, y_max)
OBSTACULOS_FIXOS = [
    (14, 17, 5, 17),
]

CENARIOS = {
    "frame0.jpg": [
        (15, 5), (15, 6), (15, 7), (14, 16), (16, 15),
        (21, 11), (9, 23), (10, 22), (8, 21), (12, 21),
        (11, 28), (9, 29), (20, 27), (22, 28), (24, 1), (27, 2),
    ],
    "frame170.jpg": [
        (15, 5), (15, 6), (15, 7), (15, 16), (17, 14),
        (20, 15), (23, 16), (15, 24), (10, 19), (9, 16),
        (6, 13), (5, 12),
    ],
    "frame339.jpg": [
        (15, 5), (15, 6), (15, 7), (14, 16), (15, 15),
        (20, 12), (23, 15), (18, 26), (5, 11), (7, 12),
    ],
}


def criar_mascara_caminhavel():
    caminhavel = np.zeros((LINHAS, COLUNAS), dtype=bool)

    for y in range(LINHAS):
        esquerda = LIMITE_ESQUERDO[y]
        direita = LIMITE_DIREITO[y]
        caminhavel[y, esquerda:direita + 1] = True

    return caminhavel


def marcar_disco(matriz, px, py, raio, valor=True):
    raio = max(0, int(raio))
    for dy in range(-raio, raio + 1):
        for dx in range(-raio, raio + 1):
            y, x = py + dy, px + dx
            if 0 <= x < COLUNAS and 0 <= y < LINHAS:
                if np.hypot(dx, dy) <= raio:
                    matriz[y, x] = valor


def criar_mapa(pessoas, agente):
    custo = np.zeros((LINHAS, COLUNAS), dtype=float)
    caminhavel = criar_mascara_caminhavel()
    bloqueados = ~caminhavel

    for x1, x2, y1, y2 in OBSTACULOS_FIXOS:
        bloqueados[y1:y2 + 1, x1:x2 + 1] = True

    for px, py in pessoas:
        if not (0 <= px < COLUNAS and 0 <= py < LINHAS):
            continue

        # O corpo é sempre obstáculo físico. Usamos uma pequena região,
        # em vez de apenas uma célula, para evitar rotas que "atropelam".
        marcar_disco(bloqueados, px, py, raio=1, valor=True)

        # A distância social continua sendo custo, não parede.
        for dy in range(-agente.raio_social, agente.raio_social + 1):
            for dx in range(-agente.raio_social, agente.raio_social + 1):
                y, x = py + dy, px + dx

                if not (0 <= x < COLUNAS and 0 <= y < LINHAS):
                    continue
                if bloqueados[y, x]:
                    continue

                dist = np.hypot(dx, dy)
                if 1 < dist <= agente.raio_social:
                    valor = (
                        agente.raio_social - dist + 1
                    ) * agente.peso_penalidade
                    custo[y, x] = max(custo[y, x], valor)

    # Os pontos de partida e chegada fazem parte da área válida do experimento.
    bloqueados[INICIO] = False
    bloqueados[OBJETIVO] = False

    return custo, bloqueados


def validar_caminho(caminho, bloqueados):
    if not caminho:
        return False

    for ponto in caminho:
        if bloqueados[ponto]:
            return False

    return True


def simular_agente_no_frame(nome_imagem, pessoas, agente):
    diretorio = os.path.dirname(os.path.abspath(__file__))
    custo, bloqueados = criar_mapa(pessoas, agente)
    caminho = a_estrela(custo, bloqueados, INICIO, OBJETIVO)

    if caminho is None:
        raise RuntimeError(
            f"Sem rota válida para {agente.nome} em {nome_imagem}"
        )

    if not validar_caminho(caminho, bloqueados):
        raise RuntimeError(
            f"Rota inválida encontrada para {agente.nome} em {nome_imagem}"
        )

    fig, ax = plt.subplots(figsize=(8, 8))
    imagem = os.path.join(diretorio, nome_imagem)

    if os.path.exists(imagem):
        ax.imshow(
            plt.imread(imagem),
            extent=[0, COLUNAS, 0, LINHAS],
        )
    else:
        ax.imshow(
            custo,
            origin="lower",
            extent=[0, COLUNAS, 0, LINHAS],
            alpha=0.6,
        )

    ax.set_xticks(np.arange(COLUNAS + 1))
    ax.set_yticks(np.arange(LINHAS + 1))
    ax.grid(linewidth=0.5, alpha=0.5)

    ax.plot(INICIO[1] + 0.5, INICIO[0] + 0.5, "go", markersize=12)
    ax.plot(OBJETIVO[1] + 0.5, OBJETIVO[0] + 0.5, "bo", markersize=12)

    for px, py in pessoas:
        ax.plot(px + 0.5, py + 0.5, "kx", markersize=8, markeredgewidth=2)
        ax.add_patch(
            plt.Circle(
                (px + 0.5, py + 0.5),
                agente.raio_social + 0.5,
                fill=False,
                linestyle="--",
                alpha=0.45,
            )
        )

    ys = [p[0] + 0.5 for p in caminho]
    xs = [p[1] + 0.5 for p in caminho]
    ax.plot(
        xs,
        ys,
        color=agente.cor_linha,
        linewidth=4,
        label=agente.nome,
    )

    ax.set_title(f"A* - {agente.nome} ({nome_imagem})")
    ax.legend()
    ax.set_xlim(0, COLUNAS)
    ax.set_ylim(0, LINHAS)

    nome = (
        agente.nome
        .replace(" ", "_")
        .replace("ô", "o")
        .replace("ç", "c")
        .replace("ã", "a")
    )
    frame = os.path.splitext(nome_imagem)[0]
    saida = os.path.join(
        diretorio,
        f"diagrama_{frame}_{nome}.png",
    )

    plt.savefig(saida, dpi=300, bbox_inches="tight")
    plt.close()

    print(
        f"{nome_imagem} | {agente.nome} | "
        f"caminho={len(caminho)} células | OK"
    )
    return caminho


def criar_agentes():
    # Com 2 células ≈ 1 m:
    # 3 células = 1,5 m; 1 célula = 0,5 m; 2 células = 1,0 m.
    return [
        Agente(
            "Robô de Limpeza",
            raio_social=3,
            peso_penalidade=4.0,
            cor_linha="blue",
            velocidade="lenta",
        ),
        Agente(
            "Pedestre Apressado",
            raio_social=1,
            peso_penalidade=0.5,
            cor_linha="red",
            velocidade="alta",
        ),
        Agente(
            "Segurança",
            raio_social=2,
            peso_penalidade=2.0,
            cor_linha="orange",
            velocidade="moderada",
        ),
    ]


if __name__ == "__main__":
    agentes = criar_agentes()

    for frame, pessoas in CENARIOS.items():
        print(f"--- {frame} ---")
        for agente in agentes:
            simular_agente_no_frame(frame, pessoas, agente)

    print("[SUCESSO] 3 frames x 3 agentes processados.")
