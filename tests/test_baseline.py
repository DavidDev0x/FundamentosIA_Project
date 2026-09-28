import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "checkin_2"))

from modelo_baseline import rodar_modelo_baseline


def test_baseline_sem_fila_quando_capacidade_suficiente(tmp_path):
    dados = pd.DataFrame({
        "cruzamento": ["A", "A"],
        "minuto": ["2026-09-28 17:00:00", "2026-09-28 17:01:00"],
        "volume_veiculos": [5, 5],
    })
    arquivo = tmp_path / "dados.csv"
    dados.to_csv(arquivo, index=False)

    resultado = rodar_modelo_baseline(arquivo, capacidade_por_minuto=10)
    linha = resultado.iloc[0]

    assert linha["fluxo_total_veiculos"] == 10
    assert linha["veiculo_minutos_em_fila"] == 0
    assert linha["fila_maxima_veiculos"] == 0
    assert linha["atraso_medio_estimado_min"] == 0


def test_baseline_acumula_fila(tmp_path):
    dados = pd.DataFrame({
        "cruzamento": ["A", "A"],
        "minuto": ["2026-09-28 17:00:00", "2026-09-28 17:01:00"],
        "volume_veiculos": [20, 20],
    })
    arquivo = tmp_path / "dados.csv"
    dados.to_csv(arquivo, index=False)

    resultado = rodar_modelo_baseline(arquivo, capacidade_por_minuto=15)
    linha = resultado.iloc[0]

    assert linha["fluxo_total_veiculos"] == 40
    assert linha["veiculo_minutos_em_fila"] == 15
    assert linha["fila_maxima_veiculos"] == 10
    assert linha["atraso_medio_estimado_min"] == 0.375
