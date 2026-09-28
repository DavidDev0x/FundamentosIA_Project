import sys
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/"atividade"))
from agente import Agente
from algoritmo import a_estrela
from main import criar_mapa

def test_desvia_de_obstaculo():
    custo=np.zeros((5,5))
    bloqueados=np.zeros((5,5), dtype=bool)
    bloqueados[2,2]=True
    caminho=a_estrela(custo,bloqueados,(0,0),(4,4))
    assert caminho is not None
    assert (2,2) not in caminho

def test_custo_social_nao_vira_parede():
    agente=Agente("Teste",3,50,"blue")
    custo,bloqueados=criar_mapa([(10,10),(11,10)],agente)
    assert bloqueados[10,10]
    assert custo[10,12] > 0
    assert not bloqueados[10,12]
