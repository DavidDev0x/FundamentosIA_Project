import pandas as pd
import os

def rodar_modelo_baseline(caminho_csv):
    """
    Simula o Modelo Baseline (Sistema de Semáforos com Tempos Fixos, sem IA).
    Lê os dados agregados e calcula o impacto do tráfego sem a intervenção 
    do Sistema Multiagentes.
    """
    print("=== INICIANDO MODELO BASELINE (SEMÁFORO FIXO / SEM IA) ===\n")
    
    try:
        df = pd.read_csv(caminho_csv)
    except FileNotFoundError:
        print(f"Erro: Arquivo {caminho_csv} não encontrado.")
        return
        
    # Ordena cronologicamente para simular a passagem do tempo
    df = df.sort_values(by=['cruzamento', 'minuto'])
    
    # Parâmetros do Baseline (Semáforo tradicional e burro)
    CAPACIDADE_POR_MINUTO = 15 # Um semáforo fixo gargala rapidamente com o fluxo simulado
    
    resultados = []
    
    # Agrupando por cruzamento para analisar o acúmulo de fila no tempo
    for cruzamento, dados in df.groupby('cruzamento'):
        fila_acumulada = 0
        total_retidos = 0
        
        for _, row in dados.iterrows():
            volume_chegando = row['volume_veiculos']
            
            # Carros tentando passar = os que chegaram agora + os que sobraram da fila anterior
            demanda_total = volume_chegando + fila_acumulada
            
            if demanda_total > CAPACIDADE_POR_MINUTO:
                carros_escoados = CAPACIDADE_POR_MINUTO
                fila_acumulada = demanda_total - CAPACIDADE_POR_MINUTO
            else:
                carros_escoados = demanda_total
                fila_acumulada = 0
                
            total_retidos += fila_acumulada
            
        # Calculando métricas finais do cruzamento
        fluxo_total = dados['volume_veiculos'].sum()
        infracoes_totais = dados['total_infracoes'].sum()
        
        # Métrica de performance: Retenção (congestionamento)
        taxa_congestionamento = (total_retidos / fluxo_total) * 100 if fluxo_total > 0 else 0
        
        resultados.append({
            'Cruzamento': cruzamento,
            'Fluxo Total (Veículos)': fluxo_total,
            'Total de Infrações': infracoes_totais,
            'Carros Retidos na Fila': total_retidos,
            'Taxa de Congestionamento (%)': round(taxa_congestionamento, 2)
        })

    # Exibindo o Relatório Final do Baseline
    print("RESULTADOS DO BASELINE (Sem Comunicação Inter-Agentes):")
    print("-" * 65)
    df_resultados = pd.DataFrame(resultados)
    print(df_resultados.to_string(index=False))
    print("-" * 65)
    
    media_congestionamento = df_resultados['Taxa de Congestionamento (%)'].mean()
    print(f"\n=> Taxa Média Global de Congestionamento: {media_congestionamento:.2f}%")
    print("\n[CONCLUSÃO DO BASELINE]")
    print("Este é o gargalo do sistema tradicional.")
    print("O objetivo do seu Sistema Multiagentes (Agente Coordenador) será atuar")
    print("dinamicamente sobre os tempos dos semáforos para reduzir esta taxa!")

if __name__ == "__main__":
    # Garante que o arquivo seja buscado na mesma pasta onde o script está
    diretorio_atual = os.path.dirname(os.path.abspath(__file__))
    caminho_dados = os.path.join(diretorio_atual, 'dados_agregados_coordenador.csv')
    rodar_modelo_baseline(caminho_dados)
