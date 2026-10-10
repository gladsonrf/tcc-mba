"""Baixa a taxa de câmbio R$/US$ (média mensal, venda) do SGS/BCB."""
import pandas as pd
import requests
from config import RAW, BCB_SGS_CAMBIO

OUT = RAW / "bcb"
OUT.mkdir(parents=True, exist_ok=True)
url = (f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{BCB_SGS_CAMBIO}/dados"
       "?formato=json&dataInicial=01/01/1997")
df = pd.DataFrame(requests.get(url, timeout=120).json())
df["mes"] = pd.to_datetime(df["data"], dayfirst=True).dt.strftime("%Y-%m")
df["cambio_brl_usd"] = df["valor"].astype(float)
df[["mes", "cambio_brl_usd"]].to_csv(OUT / "cambio_mensal.csv", index=False)
print(df.tail(3).to_string(index=False))
