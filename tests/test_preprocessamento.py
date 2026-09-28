import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "checkin_2"))

from gerador_dados_sma import limpar_dados, preprocessar_para_agentes


def test_limpeza_remove_duplicados_e_valores_invalidos():
    linha = {
        "timestamp": "2026-09-28 17:00:00",
        "id_veiculo": "V001",
        "tipo_veiculo": "Carro",
        "cruzamento": "A",
        "pos_x": 10,
        "pos_y": 10,
        "velocidade_kmh": 50,
        "aceleracao_ms2": 1,
    }
    invalida = dict(linha, id_veiculo="V002", velocidade_kmh=250)
    df = pd.DataFrame([linha, linha, invalida])

    limpo = limpar_dados(df)
    assert len(limpo) == 1
    assert limpo.iloc[0]["id_veiculo"] == "V001"


def test_mesmo_veiculo_nao_e_contado_varias_vezes_como_risco():
    linhas = []
    for segundo in range(3):
        linhas.append({
            "timestamp": f"2026-09-28 17:00:0{segundo}",
            "id_veiculo": "V001",
            "tipo_veiculo": "Carro",
            "cruzamento": "A",
            "pos_x": 10 + segundo,
            "pos_y": 10,
            "velocidade_kmh": 80,
            "aceleracao_ms2": 1,
        })

    _, agregado = preprocessar_para_agentes(pd.DataFrame(linhas))
    assert agregado.iloc[0]["volume_veiculos"] == 1
    assert agregado.iloc[0]["veiculos_risco"] == 1
    assert agregado.iloc[0]["veiculos_excesso_velocidade"] == 1
