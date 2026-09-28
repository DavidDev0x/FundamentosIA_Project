import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "atividade"))

from algoritmo import a_estrela
from main import (
    CENARIOS,
    INICIO,
    OBJETIVO,
    criar_agentes,
    criar_mapa,
    validar_caminho,
)


def test_todos_os_agentes_encontram_rota_valida():
    for pessoas in CENARIOS.values():
        for agente in criar_agentes():
            custo, bloqueados = criar_mapa(pessoas, agente)
            caminho = a_estrela(custo, bloqueados, INICIO, OBJETIVO)

            assert caminho is not None
            assert caminho[0] == INICIO
            assert caminho[-1] == OBJETIVO
            assert validar_caminho(caminho, bloqueados)


def test_rota_nao_ocupa_corpo_de_pedestre():
    for pessoas in CENARIOS.values():
        for agente in criar_agentes():
            custo, bloqueados = criar_mapa(pessoas, agente)
            caminho = a_estrela(custo, bloqueados, INICIO, OBJETIVO)

            for ponto in caminho:
                assert not bloqueados[ponto]


def test_movimento_diagonal_nao_corta_canto():
    import numpy as np

    custo = np.zeros((3, 3))
    bloqueados = np.zeros((3, 3), dtype=bool)
    bloqueados[0, 1] = True
    bloqueados[1, 0] = True

    caminho = a_estrela(custo, bloqueados, (0, 0), (2, 2))
    assert caminho is None
