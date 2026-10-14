import pandas as pd
import random
import os

class Via:
    def __init__(self, nome, capacidade_metros):
        self.nome = nome
        self.capacidade_metros = capacidade_metros
        self.fila_metros = 0
        self.demanda_futura_metros = 0 # Para a IA prever o que está chegando

class AgenteFiscalCruzamento:
    """
    Controla um cruzamento completo: Via Principal e Via Transversal.
    Aplica a PUNIÇÃO DO SEMÁFORO (Soma Zero no ciclo de 60s).
    """
    def __init__(self, id_nome, nome_principal, nome_transversal, proximo_no=None):
        self.id_nome = id_nome
        self.principal = Via(nome_principal, capacidade_metros=300)
        self.transversal = Via(nome_transversal, capacidade_metros=150)
        self.proximo_no = proximo_no # Ligação no Grafo
        
        self.ciclo_total = 60 # Ciclo de 60 segundos
        self.verde_principal = 30 # Inicia 50/50
        
    def obter_verde_transversal(self):
        return self.ciclo_total - self.verde_principal
        
    def simular_escoamento(self, fracao_agressivos_infratores):
        # O fluxo de escoamento cai se houver muitos motoristas infratores (fricção)
        fator_eficiencia = 1.0
        if fracao_agressivos_infratores > 0.3:
            fator_eficiencia = 0.7 # Trânsito trava com excesso de agressividade
            
        taxa_escoamento_m_s = 5.0 * fator_eficiencia # metros por segundo de verde
        
        # Escoa Via Principal
        capacidade_liberada_prin = self.verde_principal * taxa_escoamento_m_s
        metros_escoados = min(self.principal.fila_metros, capacidade_liberada_prin)
        self.principal.fila_metros -= metros_escoados
        
        # Escoa Via Transversal
        capacidade_liberada_trans = self.obter_verde_transversal() * taxa_escoamento_m_s
        self.transversal.fila_metros = max(0, self.transversal.fila_metros - capacidade_liberada_trans)
        
        # TRANSFERÊNCIA DE FLUXO (Grafo): Carros que saíram da via principal vão para o próximo cruzamento
        if self.proximo_no:
            self.proximo_no.principal.demanda_futura_metros += metros_escoados


class AgenteCoordenadorPreditivo:
    """
    Analisa a malha inteira, prevê congestionamentos baseado nos perfis 
    e ajusta o semáforo punindo vias menos cruciais.
    """
    def __init__(self, malha):
        self.malha = malha
        self.log = []
        
    def intervir_e_prever(self, minuto, fracao_infratores):
        for nome_cruz, agente in self.malha.items():
            # 1. Módulo Preditivo: O Coordenador soma a fila atual + o que ESTÁ CHEGANDO do cruzamento anterior
            fila_prevista = agente.principal.fila_metros + agente.principal.demanda_futura_metros
            ocupacao_prevista_prin = (fila_prevista / agente.principal.capacidade_metros) * 100
            
            # Se a IA sabe que a via tem muitos infratores, ela prevê um escoamento menor, 
            # logo ela antecipa a abertura do sinal ANTES da fila travar.
            margem_risco = 10 if fracao_infratores > 0.25 else 0
            
            acao = "Manteve Ciclo"
            if (ocupacao_prevista_prin + margem_risco) > 70:
                # 2. Trade-off (Soma zero): Puxa verde para a principal, mas pune a transversal
                agente.verde_principal = min(50, agente.verde_principal + 10)
                acao = f"Predição de Gargalo! Verde Principal={agente.verde_principal}s / Transversal={agente.obter_verde_transversal()}s"
            
            elif ocupacao_prevista_prin < 30 and agente.transversal.fila_metros > 50:
                # Principal está livre e Transversal tem fila: Dá tempo pra transversal
                agente.verde_principal = max(10, agente.verde_principal - 10)
                acao = f"Alívio Transversal. Verde Principal={agente.verde_principal}s / Transversal={agente.obter_verde_transversal()}s"
                
            self.log.append({
                'Minuto': minuto,
                'Cruzamento': nome_cruz,
                'Ocupacao_Real_%': round((agente.principal.fila_metros / agente.principal.capacidade_metros)*100, 1),
                'Ocupacao_Prevista_%': round(ocupacao_prevista_prin, 1),
                'Acao_Preditiva': acao
            })


def executar_simulacao_v2():
    print("=== INICIANDO SIMULADOR V2 (GRAFO, PUNIÇÃO E PREDIÇÃO) ===")
    
    # 1. Configurando o Grafo da Cidade (A -> B -> C)
    no_C = AgenteFiscalCruzamento("Node_C", "Av. Hermes Fontes", "Rua Transv. 3", proximo_no=None)
    no_B = AgenteFiscalCruzamento("Node_B", "Av. Tancredo Neves", "Rua Transv. 2", proximo_no=no_C)
    no_A = AgenteFiscalCruzamento("Node_A", "Av. Beira Mar", "Rua Transv. 1", proximo_no=no_B)
    
    malha = {"Node_A": no_A, "Node_B": no_B, "Node_C": no_C}
    coordenador = AgenteCoordenadorPreditivo(malha)
    
    # Simulando 10 minutos de tráfego intenso
    for minuto in range(1, 11):
        # Sorteando o perfil de comportamento da cidade neste minuto (Módulo Preditivo usa isso)
        fracao_infratores = random.uniform(0.1, 0.4) # Entre 10% e 40% de motoristas ruins
        
        # 2. Injetando tráfego no início da malha (Node A) e nas transversais
        demanda_chegando_A_metros = random.uniform(100, 250)
        no_A.principal.demanda_futura_metros += demanda_chegando_A_metros
        
        for no in malha.values():
            no.transversal.fila_metros += random.uniform(20, 80) # Transversais sempre enchendo
            
        # 3. O Coordenador faz as predições e ajusta os ciclos semafóricos ANTES do fluxo ocorrer
        coordenador.intervir_e_prever(minuto, fracao_infratores)
        
        # 4. As filas se movem e transferem fluxo entre si
        for no in malha.values():
            # A demanda que chegou vira fila real agora
            no.principal.fila_metros += no.principal.demanda_futura_metros
            no.principal.demanda_futura_metros = 0 # Limpa para o próximo ciclo
            
            # Escoa os carros baseado no tempo de verde definido pela IA
            no.simular_escoamento(fracao_infratores)
            
    # Salva os resultados
    df_log = pd.DataFrame(coordenador.log)
    print("\n[LOG DO COORDENADOR PREDITIVO]")
    print(df_log.to_string(index=False))
    
    diretorio_atual = os.path.dirname(os.path.abspath(__file__))
    df_log.to_csv(os.path.join(diretorio_atual, 'log_sma_v2.csv'), index=False)

if __name__ == "__main__":
    executar_simulacao_v2()
