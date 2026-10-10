"""Junta as fontes em um painel mensal (produto × mês) em data/processed/painel_mensal.csv."""
import pandas as pd
from config import RAW, PROCESSED, POSICOES

PROCESSED.mkdir(parents=True, exist_ok=True)
imp = pd.read_csv(RAW / "comexstat" / "importacao_sh4_mensal.csv", dtype={"headingCode": str})
imp["mes"] = imp["ano"].astype(str) + "-" + imp["mes"].astype(int).map("{:02d}".format)
imp = imp.rename(columns={"headingCode": "posicao"})[["mes", "posicao", "fob_usd", "kg", "preco_usd_t"]]
imp["grupo"] = imp["posicao"].map(POSICOES)

pink = pd.read_csv(RAW / "worldbank" / "pinksheet_mensal.csv")
cambio = pd.read_csv(RAW / "bcb" / "cambio_mensal.csv")
gpr = pd.read_csv(RAW / "gpr" / "gpr_mensal.csv")
gpr["mes"] = pd.to_datetime(gpr["month"]).dt.strftime("%Y-%m")
gpr_cols = ["mes"] + [c for c in ["GPR", "GPRT", "GPRA", "GPRC_RUS", "GPRC_UKR", "GPRC_SAU", "GPRC_ISR",
                                  "GPRC_CAN", "GPRC_CHN", "GPRC_EGY"] if c in gpr.columns]

painel = (imp.merge(pink, on="mes", how="left")
             .merge(cambio, on="mes", how="left")
             .merge(gpr[gpr_cols], on="mes", how="left")
             .sort_values(["posicao", "mes"]))
painel.to_csv(PROCESSED / "painel_mensal.csv", index=False)
print(painel.groupby("posicao").size(), painel.columns.tolist())
