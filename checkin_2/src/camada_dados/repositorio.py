import pandas as pd
import os

class RepositorioLog:
    """
    Camada de Dados / Infraestrutura: Responsável por I/O.
    Só este arquivo sabe como ler e escrever no disco.
    """
    def __init__(self, diretorio_base=None):
        if diretorio_base is None:
            # Sobe dois níveis para sair de src/camada_dados/ e acessar checkin_2/
            self.diretorio_base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        else:
            self.diretorio_base = diretorio_base
            
    def salvar_log_coordenador(self, lista_dicionarios):
        df_log = pd.DataFrame(lista_dicionarios)
        caminho_salvar = os.path.join(self.diretorio_base, 'log_sma_v2_camadas.csv')
        df_log.to_csv(caminho_salvar, index=False)
        return caminho_salvar

    def ler_log_coordenador(self):
        caminho_ler = os.path.join(self.diretorio_base, 'log_sma_v2_camadas.csv')
        try:
            return pd.read_csv(caminho_ler)
        except FileNotFoundError:
            return None
