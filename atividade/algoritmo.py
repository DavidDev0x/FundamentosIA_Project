import numpy as np
import heapq

def heuristica(a, b):
    """Calcula a Distância Euclidiana entre dois pontos."""
    return np.sqrt((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2)

def a_estrela(grid, inicio, objetivo):
    """
    Motor de busca que encontra o caminho mais barato (menor g(n) + h(n)).
    """
    vizinhos = [(0,1), (0,-1), (1,0), (-1,0), (1,1), (1,-1), (-1,1), (-1,-1)]
    close_set = set()
    came_from = {}
    
    gscore = {inicio: 0}
    fscore = {inicio: heuristica(inicio, objetivo)}
    
    oheap = []
    heapq.heappush(oheap, (fscore[inicio], inicio))
    
    while oheap:
        current = heapq.heappop(oheap)[1]
        
        # Se chegou ao destino, reconstrói o caminho de trás para frente
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
                
                penalidade = grid[vizinho[0]][vizinho[1]]
                if penalidade >= 100: # Barreira física
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
