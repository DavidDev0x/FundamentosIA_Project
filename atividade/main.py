import numpy as np
import matplotlib.pyplot as plt
import os

# Importando nossos módulos (Isso deixa o main.py muito mais limpo!)
from agente import Agente
from algoritmo import a_estrela

def simular_agente_no_frame(nome_imagem, pessoas, agente):
    print(f"Gerando simulação visual: {agente.nome}...")
    linhas, colunas = 30, 30
    grid = np.zeros((linhas, colunas))

    # Construindo o mapa de Força Social baseado no Agente injetado
    for px, py in pessoas:
        if 0 <= py < linhas and 0 <= px < colunas:
            grid[py][px] = 100 
            raio = agente.raio_social
            for i in range(-raio, raio + 1):
                for j in range(-raio, raio + 1):
                    if 0 <= py+i < linhas and 0 <= px+j < colunas:
                        if grid[py+i][px+j] < 100:
                            dist = np.sqrt(i**2 + j**2)
                            if dist <= raio:
                                grid[py+i][px+j] += (raio - dist + 1) * agente.peso_penalidade 

    inicio = (1, 15)
    objetivo = (28, 15)
    
    # Chama o motor de busca passando o grid modificado
    caminho = a_estrela(grid, inicio, objetivo)

    # Localiza o caminho correto da imagem relativo ao script
    diretorio_atual = os.path.dirname(os.path.abspath(__file__))
    caminho_imagem = os.path.join(diretorio_atual, nome_imagem) if not os.path.isabs(nome_imagem) else nome_imagem

    # Plotagem (Renderização do Gráfico)
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
        circle = plt.Circle((px + 0.5, py + 0.5), agente.raio_social + 0.5, color='red', fill=False, linestyle='--', alpha=0.5)
        ax.add_patch(circle)

    if caminho:
        y_coords = [p[0] + 0.5 for p in caminho]
        x_coords = [p[1] + 0.5 for p in caminho]
        ax.plot(x_coords, y_coords, color=agente.cor_linha, linewidth=4, label=f'{agente.nome}')

    plt.title(f'A* - {agente.nome} ({nome_imagem})')
    plt.legend()
    plt.xlim(0, colunas)
    plt.ylim(0, linhas)
    
    nome_seguro = agente.nome.replace(" ", "_").replace("ô", "o")
    prefixo_frame = os.path.splitext(os.path.basename(nome_imagem))[0]
    nome_saida = os.path.join(diretorio_atual, f"diagrama_{prefixo_frame}_{nome_seguro}.png")
    plt.savefig(nome_saida, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Salvo: {nome_saida}")


if __name__ == '__main__':
    # 1. Instanciamos os objetos (Injeção de Dependências)
    robo = Agente("Robô de Limpeza", raio_social=3, peso_penalidade=20, cor_linha='blue')
    apressado = Agente("Pedestre Apressado", raio_social=1, peso_penalidade=2, cor_linha='red')
    seguranca = Agente("Segurança", raio_social=2, peso_penalidade=10, cor_linha='orange')
    agentes = [robo, apressado, seguranca]

    # 2. Definimos o Estado do Ambiente (Obstáculos dos Frames 0, 170 e 339)
    cenarios = {
        'frame0.jpg': [(15, 5), (15, 6), (15, 7), (14, 16), (16, 15), (21, 11), (9, 23), (10, 22), (8, 21), (12, 21), (11, 28), (9, 29), (20, 27), (22, 28), (24, 1), (27, 2)],
        'frame170.jpg': [(15,5), (15,6), (15,7), (15,16), (17,14), (20,15), (23,16), (15,24), (10,19), (9,16), (6,13), (5,12)],
        'frame339.jpg': [(15,5), (15,6), (15,7), (14,16), (15,15), (20,12), (23,15), (18,26), (5,11), (7,12)]
    }

    # 3. Executamos as simulações para todos os cenários e agentes
    print("Iniciando simulações na arquitetura modularizada...\n")
    for nome_imagem, obstaculos in cenarios.items():
        print(f"\n--- Processando {nome_imagem} ---")
        for agente in agentes:
            simular_agente_no_frame(nome_imagem, obstaculos, agente)
    
    print("\n[SUCESSO] Projeto executado com sucesso! Arquivos salvos na pasta atividade.")
