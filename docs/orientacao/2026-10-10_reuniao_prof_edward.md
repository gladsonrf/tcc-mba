# Reunião de orientação – 10/10/2026 (Prof. Edward)

Apresentação do pré-projeto (reunião coletiva). Próximas reuniões individuais.

## Comentários do orientador

1. **Quebra estrutural** em 2022 (ureia e potássio): pico no auge do conflito e retorno em 2023.
2. **Sazonalidade**: a ureia internacional parece ter "picos e voltas"; os demais são mais suaves.
3. **Choque de 2026 (Ormuz)**: parece afetar só a ureia (rota do Golfo).
4. **Objetivo entendido**: prever fora da amostra nos períodos pré e pós-conflito, comparar com o realizado (menor erro
   quadrático médio) e ter o melhor modelo para conflitos futuros. "Ideia bastante plausível."
5. **Safra e entressafra**: a compra de fertilizantes acontece no pré-plantio; a previsão precisa captar esse período.
6. **Delimitar produtos**: são muitas culturas. Olhar no ComexStat os principais produtos exportados do agro, montar uma
   planilha com calendário de plantio e colheita. Sugestão: fazer para todos e robustez para a soja.
7. **Justificativa**: trocar "instituições de crédito rural" por **Plano Safra** (policy makers que formulam o plano).
8. **Cronograma**: semana 1 começa na semana de 12/10; coleta já feita — pode enviar ao orientador.
9. Tem interesse também no tema alternativo (Pé-de-Meia).

## O que os dados mostram (verificação feita após a reunião)

| Ponto | Evidência | Leitura |
|---|---|---|
| Quebra 2022 | Nitrogenados BR: 230 (2019) → 495 (2022) → 263 US$/t (2024–25); potássicos: 325 → 705 → 284; NPK/fosfatados: 357 → 784 → 531 | N e K: pico temporário. Fosfatados: mudança de patamar |
| Sazonalidade | Teste de dummies mensais na variação do preço (2000–2025): ureia p = 0,14; KCl p = 0,92; DAP p = 0,002; NPK BR p = 0,016 | Volume importado é sazonal; preço, pouco (exceto fosfatados) |
| Choque 2026 | Ureia +106%, nitrogenados BR +45%; KCl +11%, potássicos BR +12%; DAP e NPK BR +28% | Atinge N e P (Golfo); não atinge K |
| Pré-plantio | Volume importado: K e NPK concentram mai–set (~10–11%/mês); N concentra set–dez | Janela de compra difere por fertilizante |
| Soja | Fixação biológica de N: usa sobretudo P e K | "Robustez para soja" = KCl + MAP na janela pré-plantio |

## Plano de ação

| Prazo | Ação | Status |
|---|---|---|
| 12/10 | Enviar convite: quarta 14/10, 9h (alternativa: sábado 17/10) | [x] enviado |
| 12/10 | Subir repositório no GitHub e enviar o link | [x] https://github.com/gladsonrf/tcc-mba |
| 14/10 | Planilha de culturas (`data/external/culturas_fertilizantes.xlsx`) | [x] |
| 14/10 | Desagregar séries por NCM (ureia, KCl, MAP) | [x] dados baixados |
| 14/10 | Análise exploratória curta: quebras, sazonalidade, choque por produto | [x] notebooks/01_analise_exploratoria.ipynb |
| 14/10 | Atualizar slides (Plano Safra, produtos, quebras, cronograma) | [x] |
| Semana 2 | GPR ponderado pela origem; métrica de erro na janela de compra | [ ] |
| Semana 3 | Relatório de viabilidade dos dados | [ ] |

## Para levar à próxima reunião

- Validar: um modelo por fertilizante + robustez da soja (KCl e MAP na janela pré-plantio).
- Pedir datas de qualificação e defesa.

## Resultados da análise exploratória (notebooks/01_analise_exploratoria.ipynb)

| Ponto | Resultado por produto (ureia, KCl, MAP) | Decisão para a modelagem |
|---|---|---|
| Choques | 2024–25 vs 2019: ureia +31%, KCl −13%, MAP +64%. Ormuz 2026 (jan→pico): ureia +47%, MAP +29%, KCl +13% | Um modelo por fertilizante |
| Quebras | Regime de alta volatilidade 2021–set/2023 (KCl ~11%/mês, MAP ~10%) vs ~3% fora dele; ureia volátil desde 2021. Chow (AR(1)) só rejeita em 2008 | Tratar 2021–23 como regime de volatilidade; avaliar erro por regime |
| Sazonalidade | Preço não sazonal (F: p = 0,40; 0,70; 0,37; STL ≈ 0). Volume na janela de compra: 44–51% do ano | ARIMA (não SARIMA) como baseline; erro ponderado pela janela |
| Defasagem | Correlação máxima: ureia k = 2 (0,17), KCl k = 2 (0,38), MAP k = 3 (0,59) | Preço internacional defasado 1–3 meses como preditor |
| Estacionariedade | Log do preço I(1) (ADF não rejeita; KPSS rejeita em nível) | Modelar a 1ª diferença do log |

Atenção: a ureia tem um valor atípico em 2003 (queda isolada) que gera a falsa "volatilidade" de 2001–2003. Tratar como outlier.

## Próximos passos (semana 1–2)

| Prazo | Ação | Status |
|---|---|---|
| 14/10 | Reunião: validar desenho por fertilizante, regime de volatilidade e janela de compra | [ ] |
| 14/10 | Pedir datas de qualificação e defesa | [ ] |
| Semana 2 | GPR ponderado pela origem das importações (por produto) | [ ] |
| Semana 2 | Baselines (ingênuo, ARIMA) com validação por origem móvel | [ ] |
| Semana 3 | Relatório de viabilidade dos dados | [ ] |
