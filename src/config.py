"""Configurações e caminhos do projeto."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RAW = DATA / "raw"
INTERIM = DATA / "interim"
PROCESSED = DATA / "processed"
EXTERNAL = DATA / "external"
FIGURES = ROOT / "reports" / "figures"
TABLES = ROOT / "reports" / "tables"

# Período de análise
INICIO = "1997-01"
FIM = "2026-08"  # atualizar quando houver novos meses no ComexStat

# Séries-alvo (posições SH4 do capítulo 31 da NCM)
POSICOES = {
    "3102": "Nitrogenados",
    "3104": "Potássicos",
    "3105": "NPK, MAP, DAP e outros (mistos)",
}

# Produtos específicos (NCM 8 dígitos) para robustez — conferir no ComexStat
NCM_PRODUTOS = {
    "31021010": "Ureia (N > 45%)",
    "31022100": "Sulfato de amônio",
    "31042010": "Cloreto de potássio (K2O <= 60%) – volume pequeno",
    "31042090": "Outros cloretos de potássio – principal NCM de KCl (13,5 Mt em 2025)",
    "31054000": "MAP (fosfato monoamônico)",
    "31053000": "DAP (fosfato diamônico) – série com muitos meses vazios",
}

COMEXSTAT_URL = "https://api-comexstat.mdic.gov.br/general?language=pt"
# Pink Sheet (Banco Mundial): o link muda a cada atualização mensal.
# Pegue o link "Monthly prices" em https://www.worldbank.org/en/research/commodity-markets
PINKSHEET_URL = ("https://thedocs.worldbank.org/en/doc/74e8be41ceb20fa0da750cda2f6b9e4e-0050012026/"
                 "related/CMO-Historical-Data-Monthly.xlsx")
GPR_URL = "https://www.matteoiacoviello.com/gpr_files/data_gpr_export.xls"
BCB_SGS_CAMBIO = 3698  # Taxa de câmbio R$/US$ (venda), média mensal
