import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "checkin_2"))

from agentes_sma import AgenteCoordenador, AgenteFiscal
from gerador_dados_sma import gerar_dados_sinteticos, preprocessar_para_agentes


def test_geracao_reprodutivel():
    a = gerar_dados_sinteticos(5, semente=42)
    b = gerar_dados_sinteticos(5, semente=42)
    pd.testing.assert_frame_equal(a, b)


def test_risco_nao_ultrapassa_volume():
    bruto = gerar_dados_sinteticos(30, semente=42)
    _, agregado = preprocessar_para_agentes(bruto)
    assert (agregado["veiculos_risco"] <= agregado["volume_veiculos"]).all()


def test_comunicacao_basica():
    fiscal = AgenteFiscal("No_A_Centro")
    coordenador = AgenteCoordenador()
    mensagem = fiscal.criar_mensagem(
        {
            "minuto": "2026-09-28 17:00:00",
            "volume_veiculos": 20,
            "velocidade_media": 52.0,
            "veiculos_risco": 3,
        }
    )
    coordenador.receber(mensagem)
    assert coordenador.priorizar_cruzamento() == "No_A_Centro"
