import os

import pandas as pd

from agentes_sma import AgenteCoordenador, AgenteFiscal


def executar_demonstracao(caminho_csv=None):
    diretorio = os.path.dirname(os.path.abspath(__file__))
    caminho_csv = caminho_csv or os.path.join(
        diretorio, "dados_agregados_coordenador.csv"
    )

    dados = pd.read_csv(caminho_csv)
    obrigatorias = {
        "cruzamento",
        "minuto",
        "volume_veiculos",
        "velocidade_media",
        "veiculos_risco",
    }
    faltantes = obrigatorias.difference(dados.columns)
    if faltantes:
        raise ValueError(
            f"Colunas obrigatórias ausentes: {', '.join(sorted(faltantes))}"
        )

    dados["minuto"] = pd.to_datetime(dados["minuto"])
    minuto_demo = dados["minuto"].min()
    janela = dados[dados["minuto"] == minuto_demo].copy()

    coordenador = AgenteCoordenador()

    print("=== DEMONSTRAÇÃO DA COMUNICAÇÃO ENTRE AGENTES ===")
    print(f"Janela analisada: {minuto_demo}\n")

    for _, linha in janela.iterrows():
        fiscal = AgenteFiscal(linha["cruzamento"])
        mensagem = fiscal.criar_mensagem(linha)
        coordenador.receber(mensagem)

        print(
            f"{mensagem.cruzamento} -> Coordenador | "
            f"volume={mensagem.volume_veiculos}, "
            f"risco={mensagem.veiculos_risco}, "
            f"velocidade_media={mensagem.velocidade_media:.2f} km/h"
        )

    print("\nRanking de prioridade:")
    for posicao, mensagem in enumerate(coordenador.ranking_prioridade(), start=1):
        pressao = coordenador.calcular_pressao(mensagem)
        print(f"{posicao}. {mensagem.cruzamento} | pressão={pressao:.2f}")

    prioridade = coordenador.priorizar_cruzamento()
    print(f"\nCruzamento priorizado pelo coordenador: {prioridade}")
    return prioridade


if __name__ == "__main__":
    executar_demonstracao()
