"""Baselines de previsão (ingênuo, ingênuo sazonal, ARIMA) com validação por origem móvel.

Uso:
  python 09_baselines.py --prever Ureia      # gera previsões de um produto (cache em data/interim/)
  python 09_baselines.py --prever todos
  python 09_baselines.py --avaliar           # métricas, recortes por regime/janela de compra e teste DM

Desenho:
- Alvo: preço médio de importação (US$/t) de ureia, KCl e MAP (ComexStat), mensal.
- Treino: janela expansiva a partir de 2000-01; origens de 2010-01 a 2026-05; horizontes h = 1, 2, 3.
- ARIMA(p,1,q) no log do preço, p,q em {0,1,2}, ordem escolhida por AIC a cada janeiro, reestimado a cada origem.
- Outliers isolados (|Δlog| > 0,4 com reversão no mês seguinte) são interpolados antes da modelagem.
"""
import argparse
import itertools
import warnings
import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.tsa.arima.model import ARIMA
from config import RAW, INTERIM, TABLES, FIGURES

warnings.filterwarnings("ignore")
PRODUTOS = ["Ureia", "KCl", "MAP"]
NCM = {"31021010": "Ureia", "31042090": "KCl", "31042010": "KCl", "31054000": "MAP"}
INICIO_TREINO, PRIMEIRA_ORIGEM, ULTIMA_ORIGEM = "2000-01", "2010-01", "2026-05"
H = [1, 2, 3]
JANELA = {"Ureia": [9, 10, 11, 12], "KCl": [5, 6, 7, 8, 9], "MAP": [5, 6, 7, 8, 9]}
REGIMES = [("Choque 2021–23", "2021-03", "2023-09"), ("Ormuz 2026", "2026-03", "2026-08")]
OUT = INTERIM / "baselines"
OUT.mkdir(parents=True, exist_ok=True)


def series():
    d = pd.read_csv(RAW / "comexstat" / "importacao_ncm_mensal.csv", dtype={"coNcm": str})
    d["mes"] = pd.PeriodIndex(d["ano"].astype(str) + "-" + d["mes"].astype(int).map("{:02d}".format), freq="M")
    d["produto"] = d["coNcm"].map(NCM)
    s = d.dropna(subset=["produto"]).groupby(["produto", "mes"])[["fob_usd", "kg"]].sum()
    preco = (s["fob_usd"] / s["kg"] * 1000).unstack(0)
    kg = s["kg"].unstack(0)
    idx = pd.period_range("1997-01", "2026-08", freq="M")
    preco = preco.reindex(idx).interpolate(limit_direction="both")
    return preco, kg.reindex(idx)


def limpa_outliers(y):
    dl = np.log(y).diff()
    sus = (dl.abs() > 0.4) & (dl.shift(-1).abs() > 0.4) & (np.sign(dl) != np.sign(dl.shift(-1)))
    y = y.copy()
    y[sus] = np.nan
    return y.interpolate(), list(map(str, y.index[sus]))


def escolhe_ordem(ly):
    melhor, aic = (1, 1, 0), np.inf
    for p, q in itertools.product([0, 1, 2], [0, 1, 2]):
        try:
            r = ARIMA(ly, order=(p, 1, q), trend="n").fit()
            if r.aic < aic:
                melhor, aic = (p, 1, q), r.aic
        except Exception:
            pass
    return melhor


def prever(prod):
    preco, _ = series()
    y, outl = limpa_outliers(preco[prod])
    y = y.loc[INICIO_TREINO:]
    ly = np.log(y)
    origens = pd.period_range(PRIMEIRA_ORIGEM, ULTIMA_ORIGEM, freq="M")
    linhas, ordem = [], None
    for o in origens:
        treino = ly.loc[:o]
        if ordem is None or o.month == 1:
            ordem = escolhe_ordem(treino)
        r = ARIMA(treino.values, order=ordem, trend="n").fit()
        fc = np.exp(r.forecast(max(H)))
        for h in H:
            alvo = o + h
            if alvo > y.index[-1]:
                continue
            linhas.append({"produto": prod, "origem": str(o), "alvo": str(alvo), "h": h, "real": y[alvo],
                           "ingenuo": y[o], "ingenuo_sazonal": y[alvo - 12], "arima": fc[h - 1],
                           "ordem_arima": f"{ordem[0]},{ordem[1]},{ordem[2]}"})
    df = pd.DataFrame(linhas)
    df.to_csv(OUT / f"previsoes_{prod}.csv", index=False)
    print(prod, "origens:", len(origens), "outliers interpolados:", outl, "ordens:", df["ordem_arima"].value_counts().to_dict())


def dm(e1, e2, h):
    """Diebold-Mariano com correção de Harvey, Leybourne e Newbold (perda quadrática). H1: modelo 2 melhor."""
    d = e1 ** 2 - e2 ** 2
    n = len(d)
    dbar = d.mean()
    gam = [np.cov(d[k:], d[:n - k])[0, 1] if k else d.var() for k in range(h)]
    var = (gam[0] + 2 * sum(gam[1:])) / n
    stat = dbar / np.sqrt(var) * np.sqrt((n + 1 - 2 * h + h * (h - 1) / n) / n)
    return stat, 1 - stats.t.cdf(stat, df=n - 1)


def metricas(g, modelos, peso=None):
    out = {}
    for m in modelos:
        e = g["real"] - g[m]
        w = np.ones(len(g)) if peso is None else peso
        out[f"{m} RMSE"] = np.sqrt(np.average(e ** 2, weights=w))
        out[f"{m} MAE"] = np.average(e.abs(), weights=w)
        out[f"{m} MAPE %"] = np.average((e.abs() / g["real"]) * 100, weights=w)
    return pd.Series(out)


def avaliar():
    _, kg = series()
    df = pd.concat([pd.read_csv(OUT / f"previsoes_{p}.csv") for p in PRODUTOS])
    df["mes_alvo"] = pd.PeriodIndex(df["alvo"], freq="M").month
    vol = kg.loc["2015-01":"2025-12"]
    part = vol.groupby(vol.index.month).sum()
    part = part / part.sum()
    modelos = ["ingenuo", "ingenuo_sazonal", "arima"]

    res = []
    for (p, h), g in df.groupby(["produto", "h"]):
        recortes = {"Todos (2010–2026)": g}
        for nome, a, b in REGIMES:
            recortes[nome] = g[(g["alvo"] >= a) & (g["alvo"] <= b)]
        recortes["Fora dos choques"] = g[~((g["alvo"] >= "2021-03") & (g["alvo"] <= "2023-09")) & (g["alvo"] < "2026-03")]
        recortes["Janela de compra"] = g[g["mes_alvo"].isin(JANELA[p])]
        for nome, gg in recortes.items():
            if len(gg) < 3:
                continue
            s = metricas(gg, modelos)
            s["produto"], s["h"], s["recorte"], s["n"] = p, h, nome, len(gg)
            res.append(s)
        # todos os meses, ponderado pelo volume do mês-alvo
        w = g["mes_alvo"].map(part[p]).values
        s = metricas(g, modelos, peso=w)
        s["produto"], s["h"], s["recorte"], s["n"] = p, h, "Ponderado pelo volume", len(g)
        res.append(s)
    res = pd.DataFrame(res)
    res = res.set_index(["produto", "h", "recorte", "n"]).round(1)
    res.to_csv(TABLES / "03_baselines_metricas.csv")

    rel = res[[c for c in res.columns if c.endswith("RMSE")]].copy()
    rel["ARIMA / ingênuo (RMSE)"] = (rel["arima RMSE"] / rel["ingenuo RMSE"]).round(3)
    rel.to_csv(TABLES / "03_baselines_rmse_relativo.csv")

    dmr = []
    for (p, h), g in df.groupby(["produto", "h"]):
        e_ing, e_ari = (g["real"] - g["ingenuo"]).values, (g["real"] - g["arima"]).values
        st, pv = dm(e_ing, e_ari, h)
        dmr.append({"produto": p, "h": h, "DM (ingênuo vs ARIMA)": round(st, 2), "p-valor (ARIMA melhor)": round(pv, 3)})
    pd.DataFrame(dmr).to_csv(TABLES / "03_teste_dm.csv", index=False)

    print(rel.xs("Todos (2010–2026)", level="recorte").to_string())
    print(pd.DataFrame(dmr).to_string(index=False))

    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(3, 1, figsize=(10, 8), sharex=True)
    for ax, p, cor in zip(axes, PRODUTOS, ["#2D6FB5", "#C96A1B", "#2E8B57"]):
        g = df[(df["produto"] == p) & (df["h"] == 3)]
        t = pd.PeriodIndex(g["alvo"], freq="M").to_timestamp()
        ax.plot(t, g["real"], color="#1F2D3D", lw=1.6, label="Realizado")
        ax.plot(t, g["ingenuo"], color="#8A94A0", lw=1.1, ls="--", label="Ingênuo (h = 3)")
        ax.plot(t, g["arima"], color=cor, lw=1.3, label="ARIMA (h = 3)")
        ax.set_title(p, loc="left", fontweight="bold"); ax.set_ylabel("US$/t")
        ax.legend(frameon=False, fontsize=9, loc="upper left"); ax.spines[["top", "right"]].set_visible(False)
        ax.grid(color="#E6EAEF")
    fig.tight_layout(); fig.savefig(FIGURES / "03_baselines_h3.png", dpi=110, bbox_inches="tight")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--prever", choices=PRODUTOS + ["todos"])
    ap.add_argument("--avaliar", action="store_true")
    a = ap.parse_args()
    if a.prever:
        for p in (PRODUTOS if a.prever == "todos" else [a.prever]):
            prever(p)
    if a.avaliar:
        avaliar()
