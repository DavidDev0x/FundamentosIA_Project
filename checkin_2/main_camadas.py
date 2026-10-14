import sys
import os

# Garante que o python consiga achar a pasta src como um módulo
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.camada_aplicacao.simulador_service import SimuladorService
from src.camada_apresentacao.visualizador import VisualizadorUI

def main():
    print("==========================================================")
    print(" SMA DE TRÂNSITO - ARQUITETURA EM CAMADAS (CLEAN ARCH)    ")
    print("==========================================================\n")
    
    # 1. Instancia e Roda a Aplicação (Negócio)
    app_service = SimuladorService()
    app_service.executar_simulacao(minutos=15)
    
    print("\n----------------------------------------------------------\n")
    
    # 2. Instancia e Roda a Apresentação (UI/Gráficos)
    ui = VisualizadorUI()
    ui.exibir_dashboard()
    
    print("\nExecução finalizada com sucesso!")

if __name__ == "__main__":
    main()
