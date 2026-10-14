# FundamentosIA Project

Projeto acadêmico de Fundamentos de Inteligência Artificial voltado à simulação de fiscalização e coordenação de tráfego por um Sistema Multiagentes (SMA).

## Estrutura

- `atividade/`: atividade anterior de agentes e busca.
- `checkin_2/`: fonte de dados simulada, pré-processamento, baseline e estrutura inicial dos agentes do projeto de trânsito.

## Executar o Projeto (Simulador SMA e Semáforo Inteligente)

Para rodar a versão final com Grafo, Predição e Visualização, instale as dependências e rode os scripts nesta ordem:

```bash
# 1. Ative o ambiente virtual e instale as dependências
pip install pandas numpy matplotlib

# 2. Gere o tráfego simulado (Visão Computacional) com os perfis físicos e ruas de Aracaju
python checkin_2/gerador_dados_sma.py

# 3. Execute o Sistema Multiagentes Avançado (Fiscal e Coordenador intervindo no trânsito)
python checkin_2/sma_v2_avancado.py

# 4. Gere o Gráfico / Dashboard visual com o log das intervenções
python checkin_2/visualizador_dashboard.py
```

A documentação da arquitetura dos Agentes está detalhada no arquivo `checkin_2/explicacao_arquitetura_v2.md`.
O relatório do Check-in encontra-se em `checkin_2/Checkin_2_Relatorio.md`.
