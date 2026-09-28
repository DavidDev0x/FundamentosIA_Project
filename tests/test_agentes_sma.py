import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "checkin_2"))

from agentes_sma import AgenteCoordenador, AgenteFiscal


def _mensagem(cruzamento, volume, risco):
    fiscal = AgenteFiscal(cruzamento)
    return fiscal.criar_mensagem({
        "minuto": "2026-09-28 17:00:00",
        "volume_veiculos": volume,
        "velocidade_media": 50.0,
        "veiculos_risco": risco,
    })


def test_coordenador_sem_mensagens():
    coordenador = AgenteCoordenador()
    assert coordenador.priorizar_cruzamento() is None


def test_pressao_considera_volume_e_risco():
    coordenador = AgenteCoordenador()
    msg = _mensagem("No_A_Centro", 10, 3)
    assert coordenador.calcular_pressao(msg) == 16.0


def test_risco_pode_mudar_prioridade():
    coordenador = AgenteCoordenador()
    coordenador.receber(_mensagem("No_A_Centro", 20, 0))
    coordenador.receber(_mensagem("No_B_Norte", 15, 5))
    assert coordenador.priorizar_cruzamento() == "No_B_Norte"


def test_ranking_decrescente():
    coordenador = AgenteCoordenador()
    coordenador.receber(_mensagem("No_A_Centro", 10, 1))
    coordenador.receber(_mensagem("No_B_Norte", 15, 1))
    coordenador.receber(_mensagem("No_C_Leste", 12, 4))
    ranking = coordenador.ranking_prioridade()
    pressoes = [coordenador.calcular_pressao(m) for m in ranking]
    assert pressoes == sorted(pressoes, reverse=True)
