import os
import matplotlib.pyplot as plt
import numpy as np
from agente import Agente
from algoritmo import a_estrela

LINHAS = COLUNAS = 30
INICIO = (1, 15)
OBJETIVO = (28, 15)

# (x_min, x_max, y_min, y_max). Ajustar pela grade se necessario.
OBSTACULOS_FIXOS = [(14, 17, 5, 17)]

CENARIOS = {
    "frame0.jpg": [(15,5),(15,6),(15,7),(14,16),(16,15),(21,11),(9,23),(10,22),(8,21),(12,21),(11,28),(9,29),(20,27),(22,28),(24,1),(27,2)],
    "frame170.jpg": [(15,5),(15,6),(15,7),(15,16),(17,14),(20,15),(23,16),(15,24),(10,19),(9,16),(6,13),(5,12)],
    "frame339.jpg": [(15,5),(15,6),(15,7),(14,16),(15,15),(20,12),(23,15),(18,26),(5,11),(7,12)],
}

def criar_mapa(pessoas, agente):
    custo = np.zeros((LINHAS, COLUNAS), dtype=float)
    bloqueados = np.zeros((LINHAS, COLUNAS), dtype=bool)

    for x1, x2, y1, y2 in OBSTACULOS_FIXOS:
        bloqueados[y1:y2+1, x1:x2+1] = True

    for px, py in pessoas:
        if 0 <= px < COLUNAS and 0 <= py < LINHAS:
            bloqueados[py, px] = True
            for dy in range(-agente.raio_social, agente.raio_social + 1):
                for dx in range(-agente.raio_social, agente.raio_social + 1):
                    y, x = py + dy, px + dx
                    if not (0 <= x < COLUNAS and 0 <= y < LINHAS):
                        continue
                    dist = np.hypot(dx, dy)
                    if 0 < dist <= agente.raio_social:
                        valor = (agente.raio_social - dist + 1) * agente.peso_penalidade
                        # MAX evita que bolhas sobrepostas virem uma parede acidental.
                        custo[y, x] = max(custo[y, x], valor)

    bloqueados[INICIO] = False
    bloqueados[OBJETIVO] = False
    return custo, bloqueados

def simular_agente_no_frame(nome_imagem, pessoas, agente):
    diretorio = os.path.dirname(os.path.abspath(__file__))
    custo, bloqueados = criar_mapa(pessoas, agente)
    caminho = a_estrela(custo, bloqueados, INICIO, OBJETIVO)
    if caminho is None:
        raise RuntimeError(f"Sem rota para {agente.nome} em {nome_imagem}")

    fig, ax = plt.subplots(figsize=(8, 8))
    imagem = os.path.join(diretorio, nome_imagem)
    if os.path.exists(imagem):
        ax.imshow(plt.imread(imagem), extent=[0, COLUNAS, 0, LINHAS])
    else:
        ax.imshow(custo, origin="lower", extent=[0,COLUNAS,0,LINHAS], alpha=.6)

    ax.set_xticks(np.arange(COLUNAS + 1)); ax.set_yticks(np.arange(LINHAS + 1))
    ax.grid(linewidth=.5, alpha=.5)
    ax.plot(INICIO[1]+.5, INICIO[0]+.5, "go", markersize=12)
    ax.plot(OBJETIVO[1]+.5, OBJETIVO[0]+.5, "bo", markersize=12)

    for px, py in pessoas:
        ax.plot(px+.5, py+.5, "kx", markersize=8, markeredgewidth=2)
        ax.add_patch(plt.Circle((px+.5,py+.5), agente.raio_social+.5,
                                fill=False, linestyle="--", alpha=.45))

    ys=[p[0]+.5 for p in caminho]; xs=[p[1]+.5 for p in caminho]
    ax.plot(xs, ys, color=agente.cor_linha, linewidth=4, label=agente.nome)
    ax.set_title(f"A* - {agente.nome} ({nome_imagem})")
    ax.legend(); ax.set_xlim(0,COLUNAS); ax.set_ylim(0,LINHAS)

    nome=agente.nome.replace(" ","_").replace("ô","o").replace("ç","c").replace("ã","a")
    frame=os.path.splitext(nome_imagem)[0]
    saida=os.path.join(diretorio, f"diagrama_{frame}_{nome}.png")
    plt.savefig(saida, dpi=300, bbox_inches="tight"); plt.close()
    print(f"{nome_imagem} | {agente.nome} | caminho={len(caminho)} celulas")
    return caminho

if __name__ == "__main__":
    agentes = [
        Agente("Robô de Limpeza", 3, 4.0, "blue"),
        Agente("Pedestre Apressado", 1, 0.5, "red"),
        Agente("Segurança", 2, 2.0, "orange"),
    ]
    for frame, pessoas in CENARIOS.items():
        print(f"--- {frame} ---")
        for agente in agentes:
            simular_agente_no_frame(frame, pessoas, agente)
    print("[SUCESSO] 3 frames x 3 agentes processados.")
