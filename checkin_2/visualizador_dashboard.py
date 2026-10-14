import pandas as pd
import matplotlib.pyplot as plt
import os

def gerar_grafico():
    print("Gerando visualização da atuação do SMA...")
    
    diretorio_atual = os.path.dirname(os.path.abspath(__file__))
    caminho_dados = os.path.join(diretorio_atual, 'log_intervencoes_sma.csv')
    
    try:
        df = pd.read_csv(caminho_dados)
    except FileNotFoundError:
        print("Log não encontrado. Rode sma_agentes.py primeiro.")
        return
        
    df['Minuto'] = pd.to_datetime(df['Minuto']).dt.strftime('%H:%M')
    cruzamentos = df['Cruzamento'].unique()
    
    # Criando um gráfico de linhas para a Ocupação
    plt.figure(figsize=(12, 6))
    
    for cruz in cruzamentos:
        dados_cruz = df[df['Cruzamento'] == cruz]
        plt.plot(dados_cruz['Minuto'], dados_cruz['Ocupacao_%'], marker='o', label=cruz.replace('_', ' '))
        
        # Destacar onde o Coordenador interveio (Aumentou Verde)
        intervencoes = dados_cruz[dados_cruz['Acao_Coordenador'].str.contains('Aumentou Verde')]
        if not intervencoes.empty:
            plt.scatter(intervencoes['Minuto'], intervencoes['Ocupacao_%'], 
                        color='red', s=150, zorder=5, label=f"Intervenção do Coordenador ({cruz})")

    # Linha de alerta de gridlock (70% de ocupação física da via)
    plt.axhline(y=70, color='r', linestyle='--', alpha=0.5, label='Risco de Gridlock (Limiar 70%)')

    plt.title('Dinâmica de Fila (Ocupação Física em %) com Sistema Multiagentes', fontsize=14)
    plt.xlabel('Tempo (Minuto)', fontsize=12)
    plt.ylabel('Ocupação da Via (%)', fontsize=12)
    plt.ylim(-5, 110)
    plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
    plt.grid(True, linestyle=':', alpha=0.6)
    
    plt.tight_layout()
    caminho_grafico = os.path.join(diretorio_atual, 'dashboard_sma.png')
    plt.savefig(caminho_grafico)
    print(f"Gráfico salvo com sucesso em: {caminho_grafico}")

if __name__ == "__main__":
    gerar_grafico()
