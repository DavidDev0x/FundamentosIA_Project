# Check-in 2 - Plataforma de Fiscalização Virtual e Simulação Preditiva baseada em SMA

## 1. Demonstração da Fonte de Dados (Datasets/APIs)
Como o escopo técnico direciona o foco para a modelagem dos Agentes, a etapa de extração via Visão Computacional foi abstraída e substituída por um **módulo gerador de dados sintéticos**. 

Criamos um script (`gerador_dados_sma.py`) que simula a saída de uma rede neural processando o fluxo de veículos nos cruzamentos.
*   **Dados Coletados pelo Agente Local:** O gerador entrega um dataset frame a frame contendo: `timestamp`, `id_veiculo`, `tipo_veiculo`, `cruzamento` (nó), `pos_x`, `pos_y`, `velocidade_kmh` e `aceleracao_ms2`.
*   **Vantagem da Geração Sintética:** Permite alimentar nosso **Módulo de Simulação de Perfis** controlando ativamente a distribuição estocástica dos perfis de motoristas (ex: 60% Prudentes, 30% Agressivos, 10% Infratores) para observar as variações na malha viária e estressar o modelo.

## 2. Estratégia de Limpeza e Pré-processamento
O pré-processamento é executado descentralizadamente por cada **Agente Fiscal Virtual (Nível Local)**, visando aliviar a carga computacional e de rede. As etapas são:

1.  **Limpeza (Data Cleansing):** Remoção de logs corrompidos (NaNs) e anomalias de sensor (ex: saltos impossíveis de localização X/Y).
2.  **Engenharia de Atributos (Feature Engineering):** O agente fiscal calcula o comportamento de risco aplicando limiares lógicos sobre os dados contínuos. Exemplo prático aplicado: 
    * Se `velocidade_kmh > 60`, cria a flag boolean `excesso_velocidade`.
    * Se `aceleracao_ms2 > 4.0`, cria a flag `aceleracao_brusca`.
    * A união dessas condições gera a feature unificada `comportamento_risco`.
3.  **Agregação e Empacotamento:** O Agente Fiscal condensa os dados frame a frame (milissegundos) em janelas temporais de 1 minuto. O payload resultante enviado via *Comunicação Inter-Agentes* para o Nível Central contém apenas dados processados: `cruzamento`, `minuto`, `volume_veiculos`, `velocidade_media`, e `total_infracoes`.

## 3. Modelo Baseline Pretendido
Para validar a eficácia do nosso Sistema Multiagentes (SMA) adaptativo, estabeleceremos como **Baseline um modelo estatístico sem autonomia e sem comunicação**.

*   **O Baseline:** Um sistema isolado de nós onde não há troca de mensagens entre os cruzamentos e nem reajuste semafórico. Ele apenas totalizará o fluxo e calculará o tempo médio de viagem utilizando um cenário estático de controle (onde 100% dos motoristas simulados possuem o perfil "Prudente").
*   **Comparativo de Sucesso:** Quando ativarmos os "Agentes Fiscais" juntamente com o "Agente Coordenador" em um cenário caótico (alta inserção de motoristas agressivos e infratores), o SMA deverá provar seu valor. A métrica de sucesso será a capacidade do modelo de intervir e apresentar **menores tempos de retenção (congestionamento)** em relação às projeções lineares que ocorreriam no modelo Baseline diante do mesmo volume de tráfego.
