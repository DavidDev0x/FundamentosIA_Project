import os

import pandas as pd

CAPACIDADE_POR_MINUTO = 15


def rodar_modelo_baseline(caminho_csv, capacidade_por_minuto=CAPACIDADE_POR_MINUTO):
    """Simula semáforos de capacidade fixa, sem comunicação ou adaptação."""
    df = pd.read_csv(caminho_csv)
    obrigatorias = {"cruzamento", "minuto", "volume_veiculos"}
    faltantes = obrigatorias.difference(df.columns)
    if faltantes:
        raise ValueError(f"Colunas obrigatórias ausentes: {', '.join(sorted(faltantes))}")

    df["minuto"] = pd.to_datetime(df["minuto"])
    df = df.sort_values(["cruzamento", "minuto"])
    resultados = []

    for cruzamento, dados in df.groupby("cruzamento"):
        fila = 0
        veiculo_minutos_em_fila = 0
        fila_maxima = 0

        for _, row in dados.iterrows():
            demanda = int(row["volume_veiculos"]) + fila
            escoados = min(demanda, capacidade_por_minuto)
            fila = demanda - escoados
            veiculo_minutos_em_fila += fila
            fila_maxima = max(fila_maxima, fila)

        fluxo_total = int(dados["volume_veiculos"].sum())
        atraso_medio_min = (
            veiculo_minutos_em_fila / fluxo_total if fluxo_total else 0.0
        )

        resultado = {
            "cruzamento": cruzamento,
            "fluxo_total_veiculos": fluxo_total,
            "veiculo_minutos_em_fila": int(veiculo_minutos_em_fila),
            "fila_maxima_veiculos": int(fila_maxima),
            "atraso_medio_estimado_min": round(atraso_medio_min, 3),
        }
        if "veiculos_risco" in dados.columns:
            resultado["veiculos_risco"] = int(dados["veiculos_risco"].sum())
        resultados.append(resultado)

    return pd.DataFrame(resultados)


if __name__ == "__main__":
    diretorio = os.path.dirname(os.path.abspath(__file__))
    caminho = os.path.join(diretorio, "dados_agregados_coordenador.csv")
    resultado = rodar_modelo_baseline(caminho)

    print("=== BASELINE: SEMÁFOROS FIXOS / SEM COMUNICAÇÃO ===\n")
    print(resultado.to_string(index=False))
    print("\nMétricas principais:")
    print("- veículo-minutos em fila: soma do tamanho da fila ao longo do tempo")
    print("- fila máxima: maior fila observada")
    print("- atraso médio estimado: veículo-minutos em fila / fluxo total")
