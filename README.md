# Previsão do preço de importação de fertilizantes no Brasil

TCC do MBA em Ciência de Dados Aplicada a Negócios (UFC).
**Autor:** Gladson · **Orientador:** Prof. Edward · **Repositório:** https://github.com/gladsonrf/tcc-mba

## Pergunta

É possível prever, com 1 a 3 meses de antecedência e erro menor que o de modelos ingênuos, o preço de
importação de fertilizantes no Brasil usando indicadores de risco geopolítico e de mercado?

- **Tipo de pergunta:** preditiva · **Variante:** relatório analítico
- **Unidade:** fertilizante × mês (jan/1997 – ago/2026)
- **Decisão apoiada:** momento e volume de compra de fertilizantes; subsídio ao Plano Safra

## Estrutura

```
21-tccmba/
├── data/
│   ├── raw/            # dados como baixados (ComexStat, Banco Mundial, GPR, BCB)
│   ├── interim/        # cache e etapas intermediárias (não versionado)
│   ├── processed/      # base analítica: painel_mensal.csv
│   └── external/       # planilha de culturas e calendário agrícola
├── src/                # scripts do pipeline (rodar em ordem ou via run_all.py)
├── notebooks/          # 01_analise_exploratoria, 02_gpr_e_baselines; próximos: modelos com exógenas
├── reports/
│   ├── figures/        # figuras do relatório
│   └── tables/         # tabelas de resultados
├── docs/
│   ├── ficha/          # ficha de intenção de tema
│   ├── apresentacoes/  # pré-projeto e apresentações
│   └── orientacao/     # registros das reuniões de orientação
├── references/         # bibliografia (.bib)
└── tests/
```

## Como reproduzir

```bash
pip install -r requirements.txt
cd src
python run_all.py
python 09_baselines.py --prever todos
python 09_baselines.py --avaliar
```

| Script | O que faz | Saída |
|---|---|---|
| `01_baixar_comexstat.py` | Importações mensais por posição (3102, 3104, 3105) e por NCM; origem por país | `data/raw/comexstat/` |
| `02_baixar_pinksheet.py` | Preços internacionais (ureia, KCl, DAP, gás, petróleo, soja, milho) | `data/raw/worldbank/` |
| `03_baixar_gpr.py` | Índice de Risco Geopolítico (global e por país) | `data/raw/gpr/` |
| `04_baixar_bcb.py` | Câmbio R$/US$ (SGS 3698) | `data/raw/bcb/` |
| `05_montar_base.py` | Junta tudo em um painel mensal | `data/processed/painel_mensal.csv` |
| `06_exportacoes_agro.py` | Exportações dos principais produtos do agro | `data/raw/comexstat/exportacao_agro_anual.csv` |
| `07_planilha_culturas.py` | Planilha de culturas, calendário agrícola e NCMs | `data/external/culturas_fertilizantes.xlsx` |
| `08_gpr_ponderado.py` | Risco geopolítico ponderado pela origem das importações, por fertilizante | `data/processed/gpr_ponderado.csv` |
| `09_baselines.py` | Baselines (ingênuo, ingênuo sazonal, ARIMA) com origem móvel: `--prever todos` e depois `--avaliar` | `reports/tables/03_*.csv` |

Observações:
- A API do ComexStat limita requisições; o script espera e usa cache (`data/interim/comexstat_cache`), então pode ser
  interrompido e retomado.
- O link da Pink Sheet muda todo mês: atualize `PINKSHEET_URL` em `src/config.py`.
- Atualize `FIM` em `src/config.py` quando houver novos meses.

## Fontes de dados

| Fonte | Conteúdo | Acesso |
|---|---|---|
| [ComexStat/MDIC](https://comexstat.mdic.gov.br) | Importações (FOB, kg) por NCM e país | API pública |
| [Banco Mundial – Pink Sheet](https://www.worldbank.org/en/research/commodity-markets) | Preços internacionais mensais | Planilha pública |
| [Caldara e Iacoviello – GPR](https://www.matteoiacoviello.com/gpr.htm) | Risco geopolítico mensal | Planilha pública |
| [BCB – SGS](https://www3.bcb.gov.br/sgspub) | Câmbio | API pública |
| [Conab – Calendário de plantio e colheita](https://www.gov.br/conab) | Calendário agrícola | PDF público |

Nenhuma base contém dados pessoais.

## Status

- [x] Ficha de intenção de tema (30/09/2026)
- [x] Pré-projeto apresentado (10/10/2026)
- [x] Coleta de dados (pipeline reprodutível)
- [x] Planilha de culturas e calendário agrícola
- [x] Análise exploratória: quebras estruturais, sazonalidade, choques por produto (`notebooks/01_analise_exploratoria.ipynb`)
- [x] GPR ponderado pela origem e baselines com origem móvel (`notebooks/02_gpr_e_baselines.ipynb`)
- [ ] Modelos com exógenas (SARIMAX, LASSO, gradient boosting, LSTM)
- [ ] Relatório de viabilidade dos dados (semana 3)
- [ ] Versão para qualificação (semana 8)
- [ ] Versão final (semana 10)

## Uso de IA generativa

Ferramentas de IA foram usadas como apoio à programação, à organização de leituras e à revisão de texto,
conforme as regras do curso. A declaração completa constará no relatório.
