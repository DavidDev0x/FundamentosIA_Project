import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors
import heapq
import os

# ==========================================
# 1. DEFINIÇÃO ORIENTADA A OBJETOS (AGENTES)
# ==========================================
# Aqui é onde definimos a "personalidade" e a lógica de cada agente.
class Agente:
    def __init__(self, nome, raio_social, peso_penalidade, cor_linha):
        self.nome = nome
        self.raio_social = raio_social  # Tamanho da "bolha" de conforto que ele exige
        self.peso_penalidade = peso_penalidade  # O quão "ruim" é para ele entrar na bolha de alguém
        self.cor_linha = cor_linha  # Cor para desenhar o gráfico

# Instanciando os 3 agentes com lógicas diferentes:
# 1. Robô: Conservador. Raio grande (3), foge muito de proximidade (peso 20).
robo = Agente(nome="Robô de Limpeza", raio_social=3, peso_penalidade=20, cor_linha='blue')

# 2. Apressado: Agressivo. Raio pequeno (1), não liga de passar raspando (peso 2).
apressado = Agente(nome="Pedestre Apressado", raio_social=1, peso_penalidade=2, cor_linha='red')

# 3. Segurança: Moderado. Raio médio (2), tenta manter distância normal (peso 10).
seguranca = Agente(nome="Segurança", raio_social=2, peso_penalidade=10, cor_linha='orange')


# ==========================================
# 2. ALGORITMO A* (MOTOR DE BUSCA)
# ==========================================
def heuristica(a, b):
    return np.sqrt((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2)

def a_estrela(grid, inicio, objetivo):
    vizinhos = [(0,1), (0,-1), (1,0), (-1,0), (1,1), (1,-1), (-1,1), (-1,-1)]
    close_set = set()
    came_from = {}
    gscore = {inicio: 0}
    fscore = {inicio: heuristica(inicio, objetivo)}
    oheap = []
    heapq.heappush(oheap, (fscore[inicio], inicio))
    
    while oheap:
        current = heapq.heappop(oheap)[1]
        if current == objetivo:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(inicio)
            return path[::-1]
            
        close_set.add(current)
        for i, j in vizinhos:
            vizinho = current[0] + i, current[1] + j
            if 0 <= vizinho[0] < grid.shape[0] and 0 <= vizinho[1] < grid.shape[1]:
                custo_movimento = 1.0 if (i == 0 or j == 0) else 1.414
                
                # A penalidade (g(n)) muda dependendo de qual agente está rodando!
                penalidade = grid[vizinho[0]][vizinho[1]]
                if penalidade >= 100: # 100 é barreira física (o próprio corpo da pessoa)
                    continue
                    
                tentative_g_score = gscore[current] + custo_movimento + penalidade
                if vizinho in close_set and tentative_g_score >= gscore.get(vizinho, 0):
                    continue
                if tentative_g_score < gscore.get(vizinho, 0) or vizinho not in [item[1] for item in oheap]:
                    came_from[vizinho] = current
                    gscore[vizinho] = tentative_g_score
                    fscore[vizinho] = tentative_g_score + heuristica(vizinho, objetivo)
                    heapq.heappush(oheap, (fscore[vizinho], vizinho))
    return False

# ==========================================
# 3. GERADOR DE AMBIENTE E GRÁFICO
# ==========================================
def simular_agente_no_frame(nome_imagem, pessoas, agente):
    print(f"Simulando {agente.nome} no {nome_imagem}...")
    linhas, colunas = 30, 30
    grid = np.zeros((linhas, colunas))

    # Construindo a "Força Social" baseada na personalidade do Agente atual
    for px, py in pessoas:
        if 0 <= py < linhas and 0 <= px < colunas:
            grid[py][px] = 100 # Pessoa física (Obstáculo intransponível)
            
            # Aqui o código lê o "raio social" do agente para criar a bolha
            raio = agente.raio_social
            for i in range(-raio, raio + 1):
                for j in range(-raio, raio + 1):
                    if 0 <= py+i < linhas and 0 <= px+j < colunas:
                        if grid[py+i][px+j] < 100:
                            dist = np.sqrt(i**2 + j**2)
                            if dist <= raio:
                                # Multiplica pelo peso do agente. O Robô gera um número enorme aqui, o Apressado quase nada.
                                grid[py+i][px+j] += (raio - dist + 1) * agente.peso_penalidade 

    inicio = (1, 15)
    objetivo = (28, 15)
    caminho = a_estrela(grid, inicio, objetivo)

    # Localiza o caminho correto da imagem relativo ao script
    diretorio_atual = os.path.dirname(os.path.abspath(__file__))
    caminho_imagem = os.path.join(diretorio_atual, nome_imagem) if not os.path.isabs(nome_imagem) else nome_imagem

    # Plotar
    fig, ax = plt.subplots(figsize=(8, 8))
    if os.path.exists(caminho_imagem):
        img = plt.imread(caminho_imagem)
        ax.imshow(img, extent=[0, colunas, 0, linhas])
    else:
        ax.imshow(grid, cmap='hot', origin='lower', extent=[0, colunas, 0, linhas], alpha=0.6)

    ax.set_xticks(np.arange(0, colunas, 1))
    ax.set_yticks(np.arange(0, linhas, 1))
    ax.grid(color='gray', linestyle='-', linewidth=0.5, alpha=0.5)
    ax.plot(inicio[1] + 0.5, inicio[0] + 0.5, 'go', markersize=12)
    ax.plot(objetivo[1] + 0.5, objetivo[0] + 0.5, 'bo', markersize=12)

    for px, py in pessoas:
        ax.plot(px + 0.5, py + 0.5, 'kx', markersize=8, markeredgewidth=2)
        # O desenho do círculo vermelho reflete o tamanho do raio do Agente
        circle = plt.Circle((px + 0.5, py + 0.5), agente.raio_social + 0.5, color='red', fill=False, linestyle='--', alpha=0.5)
        ax.add_patch(circle)

    if caminho:
        y_coords = [p[0] + 0.5 for p in caminho]
        x_coords = [p[1] + 0.5 for p in caminho]
        ax.plot(x_coords, y_coords, color=agente.cor_linha, linewidth=4, label=f'Rota: {agente.nome}')

    plt.title(f'A* - {agente.nome} ({nome_imagem})')
    plt.legend()
    plt.xlim(0, colunas)
    plt.ylim(0, linhas)
    
    # Salvar a imagem com o nome do agente
    nome_seguro_agente = agente.nome.replace(" ", "_").replace("ô", "o")
    prefixo_frame = os.path.splitext(os.path.basename(nome_imagem))[0]
    nome_saida = os.path.join(diretorio_atual, f"diagrama_{prefixo_frame}_{nome_seguro_agente}.png")
    plt.savefig(nome_saida, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Salvo: {nome_saida}")

# ==========================================
# 4. EXECUÇÃO PRINCIPAL
# ==========================================
# Mapeamento dos pedestres e obstáculos em cada frame
pessoas_frame0 = [(15, 5), (15, 6), (15, 7), (14, 16), (16, 15), (21, 11), (9, 23), (10, 22), (8, 21), (12, 21), (11, 28), (9, 29), (20, 27), (22, 28), (24, 1), (27, 2)]
pessoas_frame170 = [(15,5), (15,6), (15,7), (15,16), (17,14), (20,15), (23,16), (15,24), (10,19), (9,16), (6,13), (5,12)]
pessoas_frame339 = [(15,5), (15,6), (15,7), (14,16), (15,15), (20,12), (23,15), (18,26), (5,11), (7,12)]

cenarios = {
    'frame0.jpg': pessoas_frame0,
    'frame170.jpg': pessoas_frame170,
    'frame339.jpg': pessoas_frame339
}

agentes = [robo, apressado, seguranca]

if __name__ == '__main__':
    print("Iniciando simulações Orientadas a Objetos...\n")
    
    for nome_imagem, obstaculos in cenarios.items():
        print(f"\n--- Processando {nome_imagem} ---")
        for ag in agentes:
            simular_agente_no_frame(nome_imagem, obstaculos, ag)
    
    print("\n[SUCESSO] Todas as imagens dos frames 0, 170 e 339 foram geradas com sucesso!")
