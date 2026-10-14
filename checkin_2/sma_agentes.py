import pandas as pd
import os

class AgenteFiscal:
    """
    Agente Nível Local: Fica no cruzamento.
    Mede a fila com base no tamanho físico (metros) dos veículos e ajusta a ocupação.
    """
    def __init__(self, nome_cruzamento, capacidade_via_metros):
        self.nome = nome_cruzamento
        self.capacidade_via_metros = capacidade_via_metros # Quanto espaço físico tem até o cruzamento anterior
        self.fila_atual_metros = 0 
        self.tempo_verde = 30 # Segundos de verde padrão no ciclo
        
    def simular_minuto(self, volume_chegando, tamanho_total_chegando):
        # 1. Carros que chegam entram no final da fila (ocupando espaço físico)
        # Assumimos um gap extra de 1.5m entre carros parados
        espaco_extra_gap = volume_chegando * 1.5 
        demanda_metros = self.fila_atual_metros + tamanho_total_chegando + espaco_extra_gap
        
        # 2. Quanto o semáforo consegue liberar neste minuto
        # Ex: Se fica verde por 30s, e os carros andam a 5m/s (arranque), escoa X metros
        escoamento_metros_por_segundo = 5.0
        capacidade_escoamento = self.tempo_verde * escoamento_metros_por_segundo
        
        # 3. Atualiza a fila
        if demanda_metros > capacidade_escoamento:
            self.fila_atual_metros = demanda_metros - capacidade_escoamento
        else:
            self.fila_atual_metros = 0
            
        taxa_ocupacao_pct = (self.fila_atual_metros / self.capacidade_via_metros) * 100
        return min(taxa_ocupacao_pct, 100.0) # Não passa de 100% (gridlock)


class AgenteCoordenador:
    """
    Agente Nível Central: Recebe dados dos Fiscais e otimiza a malha global.
    """
    def __init__(self, agentes_fiscais):
        # Mapa dos cruzamentos monitorados
        self.malha = {agente.nome: agente for agente in agentes_fiscais}
        self.log_acoes = []
        
    def intervir(self, minuto):
        # O Coordenador se comunica com os agentes locais e toma decisões
        for nome, agente in self.malha.items():
            ocupacao = (agente.fila_atual_metros / agente.capacidade_via_metros) * 100
            
            # LÓGICA DO SMA: Intervenção Dinâmica
            if ocupacao > 70:
                # Hotspot detectado: Pede para o Agente Fiscal aumentar o verde
                agente.tempo_verde = min(60, agente.tempo_verde + 10)
                acao = f"Aumentou Verde ({agente.tempo_verde}s) - Evitando Gridlock"
            elif ocupacao < 20:
                # Via livre: Reduz o verde para ajudar outras vias do cruzamento
                agente.tempo_verde = max(15, agente.tempo_verde - 5)
                acao = f"Reduziu Verde ({agente.tempo_verde}s) - Via Ociosa"
            else:
                acao = f"Manteve Verde ({agente.tempo_verde}s)"
                
            self.log_acoes.append({
                'Minuto': minuto,
                'Cruzamento': nome,
                'Fila_Metros': round(agente.fila_atual_metros, 1),
                'Ocupacao_%': round(ocupacao, 1),
                'Acao_Coordenador': acao
            })


def rodar_sma():
    print("=== INICIANDO SISTEMA MULTIAGENTES (SMA) ===")
    
    diretorio_atual = os.path.dirname(os.path.abspath(__file__))
    caminho_dados = os.path.join(diretorio_atual, 'dados_agregados_coordenador.csv')
    
    try:
        df = pd.read_csv(caminho_dados)
    except FileNotFoundError:
        print("Dados não encontrados. Rode gerador_dados_sma.py primeiro.")
        return
        
    df = df.sort_values(by=['cruzamento', 'minuto'])
    
    # 1. Instanciando os Agentes Fiscais nas Avenidas de Aracaju
    # Dando a capacidade em metros de cada quarteirão (distância até o semáforo anterior)
    agentes_fiscais = [
        AgenteFiscal("Av_Beira_Mar_x_Tancredo", capacidade_via_metros=300),
        AgenteFiscal("Av_Rio_de_Janeiro_x_Hermes", capacidade_via_metros=250),
        AgenteFiscal("Av_Simeao_Sobral_x_Airton", capacidade_via_metros=150)
    ]
    
    # 2. Instanciando o Agente Coordenador
    coordenador = AgenteCoordenador(agentes_fiscais)
    
    # 3. Simulando a passagem do tempo
    minutos_unicos = df['minuto'].unique()
    
    for minuto in minutos_unicos:
        # Loop do minuto atual
        dados_minuto = df[df['minuto'] == minuto]
        
        for _, row in dados_minuto.iterrows():
            cruz = row['cruzamento']
            agente = coordenador.malha.get(cruz)
            
            if agente:
                # O Agente Fiscal processa a chegada física dos veículos
                agente.simular_minuto(
                    volume_chegando=row['volume_veiculos'],
                    tamanho_total_chegando=row['tamanho_total_metros']
                )
                
        # Após os Fiscais atualizarem as filas, o Coordenador age!
        coordenador.intervir(minuto)
        
    # Exibindo o resultado final
    log_df = pd.DataFrame(coordenador.log_acoes)
    print("\n[LOG DE INTERVENÇÕES DO AGENTE COORDENADOR]")
    print(log_df.to_string(index=False))
    
    caminho_log = os.path.join(diretorio_atual, 'log_intervencoes_sma.csv')
    log_df.to_csv(caminho_log, index=False)
    print(f"\n=> Log completo salvo em {caminho_log}")

if __name__ == "__main__":
    rodar_sma()
