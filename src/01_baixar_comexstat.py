"""Baixa importações mensais de fertilizantes (ComexStat) e salva em data/raw/comexstat."""
import time
import pandas as pd
from config import RAW, INICIO, FIM, POSICOES, NCM_PRODUTOS
from comexstat import consulta_cache, mensal_por_ano

OUT = RAW / "comexstat"
OUT.mkdir(parents=True, exist_ok=True)
a0, a1 = int(INICIO[:4]), int(FIM[:4])
m1 = int(FIM[5:])


def tidy(linhas, cod_col):
    df = pd.DataFrame(linhas)
    df = df.rename(columns={"year": "ano", "monthNumber": "mes", "metricFOB": "fob_usd", "metricKG": "kg"})
    df["fob_usd"] = df["fob_usd"].astype(float)
    df["kg"] = df["kg"].astype(float)
    df["preco_usd_t"] = df["fob_usd"] / df["kg"] * 1000
    return df


print("1) Posições SH4 (3102, 3104, 3105) – mensal")
df = tidy(mensal_por_ano(a0, a1, "heading", list(POSICOES), "heading", mes_fim_ultimo_ano=m1), "headingCode")
df.to_csv(OUT / "importacao_sh4_mensal.csv", index=False)

print("2) NCMs específicas – mensal")
df = tidy(mensal_por_ano(a0, a1, "ncm", list(NCM_PRODUTOS), "ncm", mes_fim_ultimo_ano=m1), "coNcm")
df.to_csv(OUT / "importacao_ncm_mensal.csv", index=False)

print("3) Capítulo 31 por país de origem – anual")
linhas = []
for ano in range(a0, a1 + 1):
    body = {"flow": "import", "monthDetail": False,
            "period": {"from": f"{ano}-01", "to": f"{ano}-{(m1 if ano == a1 else 12):02d}"},
            "filters": [{"filter": "heading", "values": list(POSICOES)}],
            "details": ["heading", "country"], "metrics": ["metricFOB", "metricKG"]}
    for l in consulta_cache(f"import_heading_country_{ano}", body):
        l["ano"] = ano
        linhas.append(l)
pd.DataFrame(linhas).to_csv(OUT / "importacao_sh4_pais_anual.csv", index=False)
print("Concluído.")
