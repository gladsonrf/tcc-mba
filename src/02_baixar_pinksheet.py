"""Baixa a Pink Sheet (Banco Mundial) e extrai preços mensais de fertilizantes e energia."""
import io
import pandas as pd
import requests
from config import RAW, PINKSHEET_URL

OUT = RAW / "worldbank"
OUT.mkdir(parents=True, exist_ok=True)
conteudo = requests.get(PINKSHEET_URL, timeout=180).content
(OUT / "CMO-Historical-Data-Monthly.xlsx").write_bytes(conteudo)

bruto = pd.read_excel(io.BytesIO(conteudo), sheet_name="Monthly Prices", header=None)
nomes = bruto.iloc[4].astype(str).str.strip()
dados = bruto.iloc[6:].copy()
dados.columns = ["mes"] + list(nomes[1:])
alvo = {"Urea": "ureia", "Potassium chloride **": "cloreto_potassio", "DAP": "dap", "TSP": "tsp",
        "Phosphate rock": "rocha_fosfatica", "Natural gas, Europe": "gas_natural_europa",
        "Natural gas, US": "gas_natural_eua", "Crude oil, Brent": "petroleo_brent",
        "Soybeans": "soja", "Maize": "milho"}
cols = {c: alvo[c] for c in dados.columns if c in alvo}
df = dados[["mes"] + list(cols)].rename(columns=cols)
df["mes"] = df["mes"].astype(str).str.replace("M", "-")
for c in cols.values():
    df[c] = pd.to_numeric(df[c], errors="coerce")
df = df.dropna(subset=["ureia"])
df.to_csv(OUT / "pinksheet_mensal.csv", index=False)
print(df.tail(3).to_string(index=False))
