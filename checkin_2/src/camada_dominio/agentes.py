from .entidades import Via

class AgenteFiscalCruzamento:
    """
    Camada de Domínio: Regras de negócio locais do nó do semáforo.
    """
    def __init__(self, id_nome, nome_principal, nome_transversal, proximo_no=None):
        self.id_nome = id_nome
        self.principal = Via(nome_principal, capacidade_metros=300)
        self.transversal = Via(nome_transversal, capacidade_metros=150)
        self.proximo_no = proximo_no
        self.ciclo_total = 60 
        self.verde_principal = 30 
        
    def obter_verde_transversal(self):
        return self.ciclo_total - self.verde_principal
        
    def simular_escoamento(self, fracao_agressivos_infratores):
        fator_eficiencia = 0.7 if fracao_agressivos_infratores > 0.3 else 1.0
        taxa_escoamento_m_s = 5.0 * fator_eficiencia 
        
        capacidade_liberada_prin = self.verde_principal * taxa_escoamento_m_s
        metros_escoados = min(self.principal.fila_metros, capacidade_liberada_prin)
        self.principal.fila_metros -= metros_escoados
        
        capacidade_liberada_trans = self.obter_verde_transversal() * taxa_escoamento_m_s
        self.transversal.fila_metros = max(0, self.transversal.fila_metros - capacidade_liberada_trans)
        
        if self.proximo_no:
            self.proximo_no.principal.demanda_futura_metros += metros_escoados


class AgenteCoordenadorPreditivo:
    """
    Camada de Domínio: Serviço de domínio que orquestra os nós do grafo.
    """
    def __init__(self, malha):
        self.malha = malha
        self.log_acoes = []
        
    def intervir_e_prever(self, minuto, fracao_infratores):
        for nome_cruz, agente in self.malha.items():
            fila_prevista = agente.principal.fila_metros + agente.principal.demanda_futura_metros
            ocupacao_prevista_prin = (fila_prevista / agente.principal.capacidade_metros) * 100
            
            margem_risco = 10 if fracao_infratores > 0.25 else 0
            acao = "Manteve Ciclo"
            
            if (ocupacao_prevista_prin + margem_risco) > 70:
                agente.verde_principal = min(50, agente.verde_principal + 10)
                acao = f"Predição de Gargalo! Verde Principal={agente.verde_principal}s / Transversal={agente.obter_verde_transversal()}s"
            elif ocupacao_prevista_prin < 30 and agente.transversal.fila_metros > 50:
                agente.verde_principal = max(10, agente.verde_principal - 10)
                acao = f"Alívio Transversal. Verde Principal={agente.verde_principal}s / Transversal={agente.obter_verde_transversal()}s"
                
            self.log_acoes.append({
                'Minuto': minuto,
                'Cruzamento': nome_cruz,
                'Ocupacao_Real_%': round((agente.principal.fila_metros / agente.principal.capacidade_metros)*100, 1),
                'Ocupacao_Prevista_%': round(ocupacao_prevista_prin, 1),
                'Acao_Preditiva': acao
            })
