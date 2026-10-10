"""Baixa o Índice de Risco Geopolítico (Caldara e Iacoviello, 2022)."""
import io
import pandas as pd
import requests
from config import RAW, GPR_URL

OUT = RAW / "gpr"
OUT.mkdir(parents=True, exist_ok=True)
conteudo = requests.get(GPR_URL, timeout=180).content
(OUT / "data_gpr_export.xls").write_bytes(conteudo)
df = pd.read_excel(io.BytesIO(conteudo))
df.to_csv(OUT / "gpr_mensal.csv", index=False)
print(df.columns[:12].tolist(), len(df))
