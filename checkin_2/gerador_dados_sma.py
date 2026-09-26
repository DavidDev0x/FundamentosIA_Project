import pandas as pd
import numpy as np
import random
import os
from datetime import datetime, timedelta

def gerar_dados_sinteticos(num_veiculos=1000):
    """
    Simula o output do módulo de Visão Computacional.
    Gera trajetórias, velocidades e acelerações para veículos em cruzamentos.
    """
    dados = []
    cruzamentos = ['No_A_Centro', 'No_B_Norte', 'No_C_Leste']
    tipos_veiculo = ['Carro', 'Moto', 'Onibus', 'Caminhao']
    
    start_time = datetime.now().replace(microsecond=0)
    
    for i in range(num_veiculos):
        id_veiculo = f"V{i:04d}"
        tipo = random.choices(tipos_veiculo, weights=[0.7, 0.15, 0.1, 0.05])[0]
        cruzamento = random.choice(cruzamentos)
        
        # O módulo de simulação varia as proporções para testar o sistema
        perfil = random.choices(['Prudente', 'Agressivo', 'Infrator'], weights=[0.6, 0.3, 0.1])[0]
        
        # Simulando 10 segundos de leitura da "câmera" para cada veículo
        tempo_base = start_time + timedelta(seconds=i) # Espaçando a entrada dos veículos
        
        for t in range(10):
            timestamp = tempo_base + timedelta(seconds=t)
            
            # Dinâmica de movimento baseada no perfil
            if perfil == 'Prudente':
                vel = np.random.normal(40, 5) # Média de 40 km/h
                acc = np.random.normal(0, 1)  # Aceleração estável
            elif perfil == 'Agressivo':
                vel = np.random.normal(65, 8) # Média de 65 km/h
                acc = np.random.normal(3, 2)  # Acelerações fortes
            else: # Infrator
                vel = np.random.normal(85, 10) # Média de 85 km/h
                acc = np.random.normal(5, 3)
                
            dados.append({
                'timestamp': timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                'id_veiculo': id_veiculo,
                'tipo_veiculo': tipo,
                'cruzamento': cruzamento,
                'pos_x': round(np.random.uniform(0, 50), 2),
                'pos_y': round(np.random.uniform(0, 50), 2),
                'velocidade_kmh': max(0, round(vel, 2)),
                'aceleracao_ms2': round(acc, 2)
            })
            
    df = pd.DataFrame(dados)
    caminho_bruto = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dados_brutos_simulacao.csv')
    df.to_csv(caminho_bruto, index=False)
    print(f"[1] Dataset bruto gerado: 'dados_brutos_simulacao.csv' ({len(df)} registros)")
    return df

def preprocessar_para_agentes(df):
    """
    Lógica interna do Agente Fiscal para limpar, classificar e agregar
    os dados antes de enviar ao Agente Coordenador.
    """
    print("\n[2] Iniciando pré-processamento (Lógica do Agente Fiscal)...")
    
    # 1. Limpeza: Garantir que não há dados corrompidos
    df_limpo = df.dropna().copy()
    
    # 2. Engenharia de Atributos: O Agente classifica o comportamento
    LIMITE_VELOCIDADE = 60 # km/h
    LIMITE_ACELERACAO = 4.0 # m/s²
    
    df_limpo['excesso_velocidade'] = (df_limpo['velocidade_kmh'] > LIMITE_VELOCIDADE).astype(int)
    df_limpo['aceleracao_brusca'] = (df_limpo['aceleracao_ms2'] > LIMITE_ACELERACAO).astype(int)
    
    # Se houver infração ou direção perigosa, marca como comportamento de risco
    df_limpo['comportamento_risco'] = ((df_limpo['excesso_velocidade'] == 1) | 
                                       (df_limpo['aceleracao_brusca'] == 1)).astype(int)
    
    caminho_limpo = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dados_limpos_agente_fiscal.csv')
    df_limpo.to_csv(caminho_limpo, index=False)
    print("    -> Features de risco extraídas. Salvo em 'dados_limpos_agente_fiscal.csv'")
    
    # 3. Agregação Temporal: Evitar gargalo de rede agrupando dados a cada minuto
    df_limpo['timestamp'] = pd.to_datetime(df_limpo['timestamp'])
    df_limpo['minuto'] = df_limpo['timestamp'].dt.floor('min')
    
    # O pacote consolidado que viaja pela comunicação inter-agentes
    dados_coordenador = df_limpo.groupby(['cruzamento', 'minuto']).agg(
        volume_veiculos=('id_veiculo', 'nunique'),
        velocidade_media=('velocidade_kmh', 'mean'),
        total_infracoes=('comportamento_risco', 'sum')
    ).reset_index()
    
    caminho_agregado = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dados_agregados_coordenador.csv')
    dados_coordenador.to_csv(caminho_agregado, index=False)
    print("[3] Pacotes de comunicação consolidados. Salvo em 'dados_agregados_coordenador.csv'")
    
    return dados_coordenador

if __name__ == "__main__":
    print("=== SIMULADOR DE FONTES DE DADOS - SMA DE TRÂNSITO ===\n")
    
    # Gera dados de 300 veículos passando pelos cruzamentos
    df_bruto = gerar_dados_sinteticos(num_veiculos=300)
    
    # Aplica o pré-processamento do Agente Fiscal
    df_agregado = preprocessar_para_agentes(df_bruto)
    
    print("\n[+] Visualização do payload recebido pelo Agente Coordenador:")
    print("-" * 70)
    print(df_agregado.head(10))
    print("-" * 70)
