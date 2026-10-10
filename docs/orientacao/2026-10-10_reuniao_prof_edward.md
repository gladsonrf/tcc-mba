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
| 12/10 | Enviar convite: quarta 14/10, 9h (alternativa: sábado 17/10) | [ ] |
| 12/10 | Subir repositório no GitHub e enviar o link | [ ] |
| 14/10 | Planilha de culturas (`data/external/culturas_fertilizantes.xlsx`) | [x] |
| 14/10 | Desagregar séries por NCM (ureia, KCl, MAP) | [x] dados baixados |
| 14/10 | Análise exploratória curta: quebras, sazonalidade, choque por produto | [ ] |
| 14/10 | Atualizar slides (Plano Safra, produtos, quebras, cronograma) | [x] |
| Semana 2 | GPR ponderado pela origem; métrica de erro na janela de compra | [ ] |
| Semana 3 | Relatório de viabilidade dos dados | [ ] |

## Para levar à próxima reunião

- Validar: um modelo por fertilizante + robustez da soja (KCl e MAP na janela pré-plantio).
- Pedir datas de qualificação e defesa.
