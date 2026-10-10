"""Índice de risco geopolítico ponderado pela origem das importações, por fertilizante.

GPR_pond[p, t] = soma_c  w[p, c, ano(t) - 1] * GPRC_c[t] / média_1985-2019(GPRC_c) * 100

- w: participação do país c no volume importado do produto p no ANO ANTERIOR (evita usar informação futura).
- GPRC: índices por país de Caldara e Iacoviello (2022). Países sem índice próprio usam um proxy regional
  (tabela PROXY); os demais usam o GPR global. A coluna `cobertura_direta` mostra o peso com índice próprio.
Saídas: data/raw/comexstat/importacao_ncm_pais_anual.csv, data/processed/gpr_ponderado.csv,
        reports/figures/02_gpr_ponderado.png, reports/tables/02_gpr_origens.csv
"""
import numpy as np
import pandas as pd
from config import RAW, PROCESSED, FIGURES, TABLES, INICIO, FIM
from comexstat import consulta_cache

PRODUTOS = {"31021010": "Ureia", "31042090": "KCl", "31042010": "KCl", "31054000": "MAP"}

DIRETO = {"Rússia": "RUS", "China": "CHN", "Canadá": "CAN", "Estados Unidos": "USA", "Alemanha": "DEU",
          "Israel": "ISR", "Arábia Saudita": "SAU", "Países Baixos (Holanda)": "NLD", "Noruega": "NOR",
          "Chile": "CHL", "Bélgica": "BEL", "Venezuela": "VEN", "Espanha": "ESP", "Reino Unido": "GBR",
          "Finlândia": "FIN", "Egito": "EGY", "Ucrânia": "UKR", "Turquia": "TUR", "Indonésia": "IDN",
          "Índia": "IND", "México": "MEX", "Polônia": "POL", "França": "FRA", "Itália": "ITA", "Tunísia": "TUN",
          "Argentina": "ARG", "Peru": "PER", "Colômbia": "COL", "Malásia": "MYS", "Japão": "JPN",
          "Coreia do Sul": "KOR", "Hungria": "HUN", "Suécia": "SWE", "Dinamarca": "DNK", "Portugal": "PRT",
          "África do Sul": "ZAF", "Vietnã": "VNM", "Tailândia": "THA", "Filipinas": "PHL", "Taiwan (Formosa)": "TWN",
          "Austrália": "AUS", "Suíça": "CHE"}
PROXY = {  # país sem índice próprio -> índices usados (média)
    "Belarus": ["RUS"], "Uzbequistão": ["RUS"], "Turcomenistão": ["RUS"], "Cazaquistão": ["RUS"],
    "Catar": ["SAU"], "Omã": ["SAU"], "Emirados Árabes Unidos": ["SAU"], "Kuweit": ["SAU"], "Bahrein": ["SAU"],
    "Irã": ["SAU", "ISR"], "Iraque": ["SAU"], "Jordânia": ["ISR"],
    "Marrocos": ["EGY", "TUN"], "Argélia": ["EGY", "TUN"], "Líbia": ["EGY", "TUN"],
}

# 1) importações por NCM e país (anual)
a0, a1, m1 = int(INICIO[:4]), int(FIM[:4]), int(FIM[5:])
linhas = []
for ano in range(a0, a1 + 1):
    body = {"flow": "import", "monthDetail": False,
            "period": {"from": f"{ano}-01", "to": f"{ano}-{(m1 if ano == a1 else 12):02d}"},
            "filters": [{"filter": "ncm", "values": list(PRODUTOS)}],
            "details": ["ncm", "country"], "metrics": ["metricFOB", "metricKG"]}
    for l in consulta_cache(f"import_ncm_country_{ano}", body):
        l["ano"] = ano
        linhas.append(l)
imp = pd.DataFrame(linhas)
imp.to_csv(RAW / "comexstat" / "importacao_ncm_pais_anual.csv", index=False)
imp["produto"] = imp["coNcm"].astype(str).map(PRODUTOS)
imp["kg"] = imp["metricKG"].astype(float)
w = imp.groupby(["produto", "ano", "country"])["kg"].sum()
w = (w / w.groupby(level=[0, 1]).transform("sum")).rename("peso").reset_index()

# 2) GPR por país normalizado (média 1985–2019 = 100)
g = pd.read_csv(RAW / "gpr" / "gpr_mensal.csv")
g["mes"] = pd.PeriodIndex(pd.to_datetime(g["month"]), freq="M")
g = g.set_index("mes")
cols = [c for c in g.columns if c.startswith("GPRC_")] + ["GPR"]
base = g.loc["1985-01":"2019-12", cols].mean()
gn = g[cols] / base * 100
gn.columns = [c.replace("GPRC_", "") for c in gn.columns]


def indice_pais(pais):
    if pais in DIRETO and DIRETO[pais] in gn.columns:
        return gn[DIRETO[pais]], "direto"
    if pais in PROXY:
        return gn[PROXY[pais]].mean(axis=1), "proxy"
    return gn["GPR"], "global"


tipo = {}
serie = {}
for pais in w["country"].unique():
    serie[pais], tipo[pais] = indice_pais(pais)
w["tipo"] = w["country"].map(tipo)

# 3) índice ponderado mensal (pesos do ano anterior; 1997 usa os próprios pesos)
meses = pd.period_range(INICIO, FIM, freq="M")
saida = []
for prod in ["Ureia", "KCl", "MAP"]:
    wp = w[w["produto"] == prod]
    for m in meses:
        ano_peso = max(m.year - 1, a0)
        wy = wp[wp["ano"] == ano_peso]
        val = sum(r.peso * serie[r.country].get(m, np.nan) for r in wy.itertuples())
        saida.append({"mes": str(m), "produto": prod, "gpr_ponderado": val,
                      "cobertura_direta": wy.loc[wy["tipo"] == "direto", "peso"].sum(),
                      "cobertura_proxy": wy.loc[wy["tipo"] == "proxy", "peso"].sum(),
                      "gpr_global": gn["GPR"].get(m, np.nan)})
out = pd.DataFrame(saida)
out.to_csv(PROCESSED / "gpr_ponderado.csv", index=False)

# 4) tabela de origens (2025) e figura
ori = (w[w["ano"] == 2025].sort_values(["produto", "peso"], ascending=[True, False])
       .groupby("produto").head(6).assign(peso=lambda d: (d["peso"] * 100).round(1)))
ori.to_csv(TABLES / "02_gpr_origens_2025.csv", index=False)
print(ori.to_string(index=False))
print(out.groupby("produto")[["cobertura_direta", "cobertura_proxy"]].mean().round(2))

import matplotlib.pyplot as plt
fig, axes = plt.subplots(3, 1, figsize=(10, 8), sharex=True)
for ax, prod, cor in zip(axes, ["Ureia", "KCl", "MAP"], ["#2D6FB5", "#C96A1B", "#2E8B57"]):
    d = out[out["produto"] == prod]
    t = pd.PeriodIndex(d["mes"], freq="M").to_timestamp()
    ax.plot(t, d["gpr_global"].rolling(3).mean(), color="#8A94A0", lw=1.2, ls="--", label="GPR global (média móvel 3m)")
    ax.plot(t, d["gpr_ponderado"].rolling(3).mean(), color=cor, lw=1.6, label=f"GPR ponderado – {prod} (média móvel 3m)")
    ax.set_title(prod, loc="left", fontweight="bold"); ax.legend(frameon=False, fontsize=9, loc="upper left")
    ax.spines[["top", "right"]].set_visible(False); ax.grid(color="#E6EAEF")
fig.tight_layout(); fig.savefig(FIGURES / "02_gpr_ponderado.png", dpi=110, bbox_inches="tight")

# 5) conteúdo preditivo exploratório: variação do índice em 3 meses vs variação futura do log do preço
ncm = pd.read_csv(RAW / "comexstat" / "importacao_ncm_mensal.csv", dtype={"coNcm": str})
ncm["mes"] = pd.PeriodIndex(ncm["ano"].astype(str) + "-" + ncm["mes"].astype(int).map("{:02d}".format), freq="M")
ncm["produto"] = ncm["coNcm"].map(PRODUTOS)
s = ncm.dropna(subset=["produto"]).groupby(["produto", "mes"])[["fob_usd", "kg"]].sum()
preco = (s["fob_usd"] / s["kg"] * 1000).unstack(0).interpolate()
out["mes"] = pd.PeriodIndex(out["mes"], freq="M")
corr = []
for prod in ["Ureia", "KCl", "MAP"]:
    gg = out[out["produto"] == prod].set_index("mes")
    y = np.log(preco[prod]).loc["2000-01":]
    for h in [1, 2, 3]:
        fut = y.shift(-h) - y
        for nome in ["gpr_ponderado", "gpr_global"]:
            x = np.log(gg[nome]).diff(3).reindex(y.index)
            corr.append({"produto": prod, "h": h, "indice": nome, "corr": round(fut.corr(x), 3)})
(pd.DataFrame(corr).pivot_table(index=["produto", "h"], columns="indice", values="corr")
   .to_csv(TABLES / "02_gpr_correlacao_preditiva.csv"))
