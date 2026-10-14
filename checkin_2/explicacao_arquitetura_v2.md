# Documentação da Arquitetura: Sistema Multiagentes (SMA) Preditivo

Este documento detalha o funcionamento do núcleo de Inteligência Artificial da nossa plataforma, que atua como um **Sistema de Semáforos Inteligentes** utilizando o conceito de Sistemas Multiagentes (SMA).

A estrutura do código foi dividida para separar a simulação do mundo real físico (carros e vias) da inteligência que controla os semáforos (Os Agentes).

---

## 1. O Mundo Físico e a Entrada de Dados

### `gerador_dados_sma.py` (Módulo de Simulação de Visão Computacional)
No projeto real, o fluxo de carros e a detecção de infrações serão feitos por câmeras rodando algoritmos de Visão Computacional (YOLO, DeepSORT). Para esta etapa, este script **simula os sensores (câmeras)**.
*   **O que faz:** Gera um tráfego estocástico de veículos (Carros, Ônibus, Motos) com **tamanhos físicos reais** em metros.
*   **Comportamento:** Ele injeta perfis de motoristas na via (`Prudente`, `Agressivo`, `Infrator`). Motoristas infratores e agressivos causam "fricção" no trânsito (acelerações bruscas), dados que serão essenciais para o módulo de predição do SMA.

---

## 2. A Inteligência (Sistema Multiagentes)

O cérebro do projeto está no arquivo **`sma_v2_avancado.py`**, composto por 3 classes principais que interagem em tempo real:

### Classe `Via` (O Espaço Físico)
Apenas a representação em código de um trecho de asfalto.
*   **O que faz:** Armazena o nome da avenida, a capacidade máxima (em metros) e a **Fila Atual** (quantos metros de asfalto estão ocupados por carros parados).
*   **Fator Preditivo:** Guarda a variável `demanda_futura_metros` (carros que estão a caminho, tendo saído do semáforo anterior).

### Agente 1: `AgenteFiscalCruzamento` (Inteligência Local)
Cada cruzamento possui um Agente Fiscal alocado.
*   **O que faz:** É o dono do semáforo local. Ele controla o cruzamento entre duas vias (A Principal e a Transversal).
*   **Comportamento - A Regra da Soma Zero:** O agente opera em um ciclo fixo de 60 segundos. Se ele der 40s de verde para a Av. Principal, ele automaticamente restringe a Av. Transversal para 20s. Ele é obrigado a fazer sacrifícios (Trade-off).
*   **Comportamento - Escoamento:** Ele calcula fisicamente quantos metros de carros ele consegue "liberar" (escoar) a cada segundo de luz verde. Carros liberados por ele viajam e são injetados no próximo `AgenteFiscal` do grafo da cidade.

### Agente 2: `AgenteCoordenadorPreditivo` (Inteligência Central)
É a "Mão Invisível" que orquestra a cidade inteira. Ele não olha para carros individuais, olha para o Grafo Urbano (Ex: Nó A conectado ao Nó B).
*   **O que faz:** Lê a situação de todos os Agentes Fiscais a cada minuto e altera o tempo de verde deles remotamente para evitar gargalos sistêmicos.
*   **Comportamento Preditivo:** Em vez de esperar a rua entupir, o coordenador soma: `Fila Atual` + `Carros a Caminho (Demanda Futura)`. Se esse total for cruzar a linha crítica de 70% da capacidade da via, ele age antes de acontecer.
*   **Interação com os Perfis:** O Coordenador recebe a taxa de motoristas `Infratores/Agressivos` do momento. Se a via estiver com muitos infratores, ele sabe que o escoamento será ineficiente (fricção) e adiciona uma **"Margem de Risco"** preventiva, abrindo o semáforo mais cedo.

---

## 3. O Fluxo do Algoritmo (Loop de Simulação)
O script `executar_simulacao_v2()` mostra exatamente o comportamento do ciclo de vida dos agentes:

1.  **Injeção de Demanda:** A cidade recebe o tráfego nas bordas (Node A e Ruas Transversais).
2.  **Predição e Ordem Central:** O Coordenador olha a malha, faz as contas de risco e ajusta os ciclos de todos os Semáforos (Agentes Fiscais) simultaneamente. *(Ex: "Node B, você vai engarrafar em 1 minuto porque o Node A mandou muitos carros. Subindo seu tempo verde para 50s").*
3.  **Movimento Físico:** Os Agentes Fiscais abrem seus semáforos com os novos tempos definidos pelo coordenador, drenando suas filas.
4.  **Transferência de Grafo:** O fluxo que passou pelo semáforo A viaja pela matriz e é contabilizado na "Demanda Futura" do semáforo B para o próximo minuto.

Com isso, o projeto deixa de ser um semáforo burro e isolado e passa a ser um **Sistema de Semáforos Inteligentes em Malha (Rede)**.
