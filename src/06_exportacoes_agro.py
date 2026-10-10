"""Exportações dos principais produtos do agro (ComexStat), para delimitar as culturas do estudo."""
import pandas as pd
from config import RAW
from comexstat import consulta_cache

PRODUTOS = {  # posição SH4 -> (produto, cultura de origem)
    "1201": ("Soja em grão", "Soja"), "2304": ("Farelo de soja", "Soja"), "1507": ("Óleo de soja", "Soja"),
    "1005": ("Milho", "Milho"), "1701": ("Açúcar", "Cana-de-açúcar"), "2207": ("Etanol", "Cana-de-açúcar"),
    "0901": ("Café", "Café"), "5201": ("Algodão", "Algodão"), "2009": ("Suco de frutas (laranja)", "Laranja"),
    "2401": ("Fumo", "Fumo"), "4703": ("Celulose", "Eucalipto/silvicultura"),
    "0202": ("Carne bovina congelada", "Pecuária"), "0207": ("Carne de frango", "Pecuária"),
    "0203": ("Carne suína", "Pecuária"),
}
ANOS = [2023, 2024, 2025]
linhas = []
for ano in ANOS:
    body = {"flow": "export", "monthDetail": False, "period": {"from": f"{ano}-01", "to": f"{ano}-12"},
            "filters": [{"filter": "heading", "values": list(PRODUTOS)}],
            "details": ["heading"], "metrics": ["metricFOB", "metricKG"]}
    for l in consulta_cache(f"export_heading_agro_{ano}", body):
        l["ano"] = ano
        linhas.append(l)
df = pd.DataFrame(linhas)
df["produto"] = df["headingCode"].map(lambda c: PRODUTOS[c][0])
df["cultura"] = df["headingCode"].map(lambda c: PRODUTOS[c][1])
df["fob_usd"] = df["metricFOB"].astype(float)
df["kg"] = df["metricKG"].astype(float)
out = RAW / "comexstat" / "exportacao_agro_anual.csv"
df[["ano", "headingCode", "produto", "cultura", "fob_usd", "kg"]].to_csv(out, index=False)
print(df.pivot_table(index="produto", columns="ano", values="fob_usd", aggfunc="sum").div(1e9).round(1)
        .sort_values(2025, ascending=False))
