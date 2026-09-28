# Check-in 2 - Plataforma de Fiscalização Virtual e Simulação Preditiva baseada em SMA

## 1. Fonte de dados

Nesta etapa o foco está na modelagem dos agentes e no fluxo de dados entre eles. A extração por visão computacional ainda não foi implementada; por isso, `gerador_dados_sma.py` produz dados sintéticos que representam a saída esperada de um módulo de detecção de veículos.

Os registros contêm `timestamp`, `id_veiculo`, `tipo_veiculo`, `cruzamento`, posição, velocidade e aceleração. Os perfis simulados permitem gerar cenários diferentes e repetir os experimentos com uma semente fixa.

A equipe também pesquisou fontes públicas para substituir ou calibrar a simulação. A SMTT de Aracaju informa em seu Portal da Transparência que ainda não formalizou uma política própria de dados abertos. O DNIT, por outro lado, disponibiliza conjuntos públicos em CSV, inclusive nas categorias **Contagem de Tráfego** e **Controle de Velocidade**. Nesta versão esses dados externos são apenas uma fonte candidata: eles ainda não foram incorporados ao código e não devem ser apresentados como dados de Aracaju.

Referências para pesquisa:
- SMTT Aracaju - Dados Abertos: https://transparencia.aracaju.se.gov.br/smtt/dados-abertos/
- DNIT - Conjuntos de Dados: https://www.gov.br/dnit/pt-br/acesso-a-informacao/dados-abertos/conjuntos-de-dados

## 2. Limpeza e pré-processamento

O `Agente Fiscal` trabalha sobre os dados do seu cruzamento. O pipeline atual:

1. remove registros incompletos e duplicados;
2. converte e valida o timestamp;
3. descarta valores fora do domínio definido para posição, velocidade e aceleração;
4. cria `excesso_velocidade` quando a velocidade simulada ultrapassa 60 km/h;
5. cria `aceleracao_brusca` quando a aceleração ultrapassa 4 m/s²;
6. combina os dois sinais em `comportamento_risco`;
7. agrega os dados por cruzamento e minuto antes do envio ao coordenador.

Um ponto importante é a diferença entre **leitura de risco** e **infração**. Como o mesmo veículo aparece em vários frames, somar as flags frame a frame contaria o mesmo veículo várias vezes. Por isso o payload passa a registrar veículos únicos sinalizados no minuto: `veiculos_excesso_velocidade`, `veiculos_aceleracao_brusca` e `veiculos_risco`. A aceleração brusca é tratada como indicador de risco, e não como infração legal por si só.

## 3. Modelo baseline

O baseline representa um sistema de semáforos com capacidade fixa, sem comunicação entre cruzamentos e sem adaptação. Ele recebe exatamente o mesmo fluxo agregado que poderá ser usado pelo SMA, permitindo uma comparação mais justa.

A capacidade inicial foi definida em 15 veículos por minuto apenas como parâmetro de simulação. As métricas são:

- **veículo-minutos em fila**: soma do tamanho da fila a cada minuto;
- **fila máxima**: maior fila observada no período;
- **atraso médio estimado**: veículo-minutos em fila dividido pelo fluxo total.

A versão anterior chamava essa razão de “taxa de congestionamento (%)”. O nome foi retirado porque o numerador mede permanência acumulada em fila e, portanto, não representa uma porcentagem de veículos congestionados.

## 4. Estrutura inicial do Sistema Multiagentes

O arquivo `agentes_sma.py` define dois papéis iniciais:

- **Agente Fiscal**: representa uma câmera/ponto de monitoramento, resume as observações locais e cria uma mensagem;
- **Agente Coordenador**: recebe mensagens dos fiscais e identifica o cruzamento com maior pressão de tráfego.

Nesta entrega a comunicação é uma abstração em Python. O reajuste de semáforos ainda é etapa futura e só deverá ser comparado ao baseline quando utilizar a mesma entrada de tráfego.

## 5. Reprodutibilidade e próximos passos

A geração sintética usa semente fixa (`42`) para que a equipe consiga repetir o mesmo experimento. As dependências mínimas estão em `requirements.txt`.

Próximas etapas previstas:

1. selecionar e documentar um conjunto real compatível com as variáveis do projeto;
2. criar um adaptador para transformar os dados reais no mesmo formato usado pelos agentes;
3. implementar a política do Agente Coordenador para ajuste de capacidade/tempo semafórico;
4. comparar baseline e SMA usando a mesma demanda;
5. registrar métricas e limitações do experimento.
