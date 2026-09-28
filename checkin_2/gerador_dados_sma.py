import os
import random
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

SEMENTE_PADRAO = 42
LIMITE_VELOCIDADE = 60.0
LIMITE_ACELERACAO = 4.0


def configurar_semente(semente=SEMENTE_PADRAO):
    random.seed(semente)
    np.random.seed(semente)


def gerar_dados_sinteticos(num_veiculos=300, semente=SEMENTE_PADRAO, inicio=None):
    """Simula leituras que futuramente poderão vir do módulo de visão computacional."""
    configurar_semente(semente)

    dados = []
    cruzamentos = ["No_A_Centro", "No_B_Norte", "No_C_Leste"]
    tipos_veiculo = ["Carro", "Moto", "Onibus", "Caminhao"]
    perfis = ["Prudente", "Agressivo", "Infrator"]
    inicio = inicio or datetime(2026, 9, 28, 17, 0, 0)

    for i in range(num_veiculos):
        id_veiculo = f"V{i:04d}"
        tipo = random.choices(tipos_veiculo, weights=[0.70, 0.15, 0.10, 0.05])[0]
        cruzamento = random.choice(cruzamentos)
        perfil = random.choices(perfis, weights=[0.60, 0.30, 0.10])[0]
        tempo_base = inicio + timedelta(seconds=i)

        # Cada veículo recebe uma direção e parte de um ponto inicial coerente.
        pos_x = np.random.uniform(5, 45)
        pos_y = np.random.uniform(5, 45)
        angulo = np.random.uniform(0, 2 * np.pi)

        for t in range(10):
            timestamp = tempo_base + timedelta(seconds=t)

            if perfil == "Prudente":
                vel = np.random.normal(40, 5)
                acc = np.random.normal(0, 1)
            elif perfil == "Agressivo":
                vel = np.random.normal(65, 8)
                acc = np.random.normal(3, 2)
            else:
                vel = np.random.normal(85, 10)
                acc = np.random.normal(5, 3)

            vel = max(0, vel)
            deslocamento = (vel / 3.6) * 0.25
            pos_x = np.clip(pos_x + np.cos(angulo) * deslocamento, 0, 50)
            pos_y = np.clip(pos_y + np.sin(angulo) * deslocamento, 0, 50)

            dados.append(
                {
                    "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                    "id_veiculo": id_veiculo,
                    "tipo_veiculo": tipo,
                    "cruzamento": cruzamento,
                    "perfil_simulado": perfil,
                    "pos_x": round(float(pos_x), 2),
                    "pos_y": round(float(pos_y), 2),
                    "velocidade_kmh": round(float(vel), 2),
                    "aceleracao_ms2": round(float(acc), 2),
                }
            )

    return pd.DataFrame(dados)


def limpar_dados(df):
    """Remove registros incompletos, duplicados e valores fora do domínio esperado."""
    colunas = [
        "timestamp", "id_veiculo", "tipo_veiculo", "cruzamento",
        "pos_x", "pos_y", "velocidade_kmh", "aceleracao_ms2"
    ]
    faltantes = [coluna for coluna in colunas if coluna not in df.columns]
    if faltantes:
        raise ValueError(f"Colunas obrigatórias ausentes: {', '.join(faltantes)}")

    df_limpo = df.dropna(subset=colunas).drop_duplicates().copy()
    df_limpo["timestamp"] = pd.to_datetime(df_limpo["timestamp"], errors="coerce")
    df_limpo = df_limpo.dropna(subset=["timestamp"])

    df_limpo = df_limpo[
        df_limpo["pos_x"].between(0, 50)
        & df_limpo["pos_y"].between(0, 50)
        & df_limpo["velocidade_kmh"].between(0, 180)
        & df_limpo["aceleracao_ms2"].between(-12, 12)
    ].copy()

    return df_limpo.sort_values(["id_veiculo", "timestamp"]).reset_index(drop=True)


def preprocessar_para_agentes(df):
    """Executa a lógica do Agente Fiscal e cria o payload para o coordenador."""
    df_limpo = limpar_dados(df)

    df_limpo["excesso_velocidade"] = (
        df_limpo["velocidade_kmh"] > LIMITE_VELOCIDADE
    ).astype(int)
    df_limpo["aceleracao_brusca"] = (
        df_limpo["aceleracao_ms2"] > LIMITE_ACELERACAO
    ).astype(int)
    df_limpo["comportamento_risco"] = (
        (df_limpo["excesso_velocidade"] == 1)
        | (df_limpo["aceleracao_brusca"] == 1)
    ).astype(int)

    # Uma leitura de risco não é automaticamente uma nova infração.
    # A agregação abaixo conta veículos únicos sinalizados no minuto.
    df_limpo["minuto"] = df_limpo["timestamp"].dt.floor("min")

    por_veiculo = (
        df_limpo.groupby(["cruzamento", "minuto", "id_veiculo"], as_index=False)
        .agg(
            velocidade_media_veiculo=("velocidade_kmh", "mean"),
            excesso_velocidade=("excesso_velocidade", "max"),
            aceleracao_brusca=("aceleracao_brusca", "max"),
            comportamento_risco=("comportamento_risco", "max"),
        )
    )

    dados_coordenador = (
        por_veiculo.groupby(["cruzamento", "minuto"], as_index=False)
        .agg(
            volume_veiculos=("id_veiculo", "nunique"),
            velocidade_media=("velocidade_media_veiculo", "mean"),
            veiculos_excesso_velocidade=("excesso_velocidade", "sum"),
            veiculos_aceleracao_brusca=("aceleracao_brusca", "sum"),
            veiculos_risco=("comportamento_risco", "sum"),
        )
    )

    dados_coordenador["velocidade_media"] = dados_coordenador["velocidade_media"].round(2)
    return df_limpo, dados_coordenador


def salvar_resultados(df_bruto, df_limpo, dados_coordenador, diretorio=None):
    diretorio = diretorio or os.path.dirname(os.path.abspath(__file__))
    df_bruto.to_csv(os.path.join(diretorio, "dados_brutos_simulacao.csv"), index=False)
    df_limpo.to_csv(os.path.join(diretorio, "dados_limpos_agente_fiscal.csv"), index=False)
    dados_coordenador.to_csv(
        os.path.join(diretorio, "dados_agregados_coordenador.csv"), index=False
    )


if __name__ == "__main__":
    print("=== SIMULADOR DE FONTES DE DADOS - SMA DE TRÂNSITO ===\n")
    df_bruto = gerar_dados_sinteticos(num_veiculos=300)
    df_limpo, df_agregado = preprocessar_para_agentes(df_bruto)
    salvar_resultados(df_bruto, df_limpo, df_agregado)

    print(f"[1] Registros brutos: {len(df_bruto)}")
    print(f"[2] Registros após limpeza: {len(df_limpo)}")
    print(f"[3] Pacotes enviados ao coordenador: {len(df_agregado)}")
    print("\nAmostra do payload do Agente Coordenador:")
    print(df_agregado.head(10).to_string(index=False))
