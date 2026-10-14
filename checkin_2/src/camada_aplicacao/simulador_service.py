import random
from src.camada_dominio.agentes import AgenteFiscalCruzamento, AgenteCoordenadorPreditivo
from src.camada_dados.repositorio import RepositorioLog

class SimuladorService:
    """
    Camada de Aplicação: Orquestra o fluxo. Pega as entidades de domínio e os repositórios
    e dita o passo a passo (Casos de Uso).
    """
    def __init__(self):
        self.repositorio = RepositorioLog()
        
    def executar_simulacao(self, minutos=10):
        print("=== [Camada de Aplicação] INICIANDO SIMULADOR V2 ===")
        
        # Instanciação do Domínio
        no_C = AgenteFiscalCruzamento("Node_C", "Av. Hermes Fontes", "Rua Transv. 3", proximo_no=None)
        no_B = AgenteFiscalCruzamento("Node_B", "Av. Tancredo Neves", "Rua Transv. 2", proximo_no=no_C)
        no_A = AgenteFiscalCruzamento("Node_A", "Av. Beira Mar", "Rua Transv. 1", proximo_no=no_B)
        
        malha = {"Node_A": no_A, "Node_B": no_B, "Node_C": no_C}
        coordenador = AgenteCoordenadorPreditivo(malha)
        
        # Loop da Simulação (Regra de Aplicação)
        for minuto in range(1, minutos + 1):
            fracao_infratores = random.uniform(0.1, 0.4) 
            
            demanda_chegando_A_metros = random.uniform(100, 250)
            no_A.principal.demanda_futura_metros += demanda_chegando_A_metros
            
            for no in malha.values():
                no.transversal.fila_metros += random.uniform(20, 80)
                
            coordenador.intervir_e_prever(minuto, fracao_infratores)
            
            for no in malha.values():
                no.principal.fila_metros += no.principal.demanda_futura_metros
                no.principal.demanda_futura_metros = 0 
                no.simular_escoamento(fracao_infratores)
                
        # Integração com a Camada de Dados
        caminho_salvo = self.repositorio.salvar_log_coordenador(coordenador.log_acoes)
        print(f"=> Simulação concluída. Log persistido em {caminho_salvo}")
