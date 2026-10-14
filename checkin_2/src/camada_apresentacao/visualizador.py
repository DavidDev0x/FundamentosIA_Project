import matplotlib.pyplot as plt
import os
from src.camada_dados.repositorio import RepositorioLog

class VisualizadorUI:
    """
    Camada de Apresentação: Lida apenas com a formatação e visualização dos dados para o usuário.
    Não possui regras de negócio.
    """
    def __init__(self):
        self.repositorio = RepositorioLog()
        
    def exibir_dashboard(self):
        print("=== [Camada de Apresentação] GERANDO DASHBOARD ===")
        df = self.repositorio.ler_log_coordenador()
        
        if df is None or df.empty:
            print("Erro: Nenhum dado encontrado para gerar o dashboard. Rode a simulação antes.")
            return
            
        cruzamentos = df['Cruzamento'].unique()
        plt.figure(figsize=(10, 5))
        
        for cruz in cruzamentos:
            dados_cruz = df[df['Cruzamento'] == cruz]
            plt.plot(dados_cruz['Minuto'], dados_cruz['Ocupacao_Real_%'], marker='o', label=cruz.replace('_', ' '))
            
            # Marca predição
            intervencoes = dados_cruz[dados_cruz['Acao_Preditiva'].str.contains('Gargalo')]
            if not intervencoes.empty:
                plt.scatter(intervencoes['Minuto'], intervencoes['Ocupacao_Real_%'], 
                            color='red', s=100, zorder=5)

        plt.axhline(y=70, color='r', linestyle='--', alpha=0.5, label='Risco de Gridlock (70%)')
        plt.title('Dinâmica de Fila (Ocupação Física em %)', fontsize=14)
        plt.xlabel('Tempo (Minuto)', fontsize=12)
        plt.ylabel('Ocupação da Via (%)', fontsize=12)
        plt.legend()
        plt.grid(True, linestyle=':', alpha=0.6)
        
        caminho_grafico = os.path.join(self.repositorio.diretorio_base, 'dashboard_sma_camadas.png')
        plt.tight_layout()
        plt.savefig(caminho_grafico)
        print(f"=> Gráfico renderizado e salvo em: {caminho_grafico}")
