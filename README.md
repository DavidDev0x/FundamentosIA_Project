# FundamentosIA Project

Projeto acadêmico de Fundamentos de Inteligência Artificial voltado à simulação de fiscalização e coordenação de tráfego por um Sistema Multiagentes (SMA).

## Estrutura

- `atividade/`: atividade anterior de agentes e busca.
- `checkin_2/`: fonte de dados simulada, pré-processamento, baseline e estrutura inicial dos agentes do projeto de trânsito.

## Executar o Check-in 2

```bash
pip install -r checkin_2/requirements.txt
python checkin_2/gerador_dados_sma.py
python checkin_2/modelo_baseline.py
```

O gerador usa semente fixa para tornar a demonstração reproduzível. Os CSVs gerados ficam dentro de `checkin_2/`.

A documentação detalhada está em `checkin_2/Checkin_2_Relatorio.md`.
