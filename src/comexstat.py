"""Cliente mínimo da API do ComexStat (MDIC), com cache por ano e espera em caso de limite (HTTP 429).

O cache (data/interim/comexstat_cache) permite interromper e retomar o download.
"""
import json
import time
import requests
from config import COMEXSTAT_URL, INTERIM

CACHE = INTERIM / "comexstat_cache"
CACHE.mkdir(parents=True, exist_ok=True)


def consulta(body: dict, tentativas: int = 8, espera: float = 12.0) -> list:
    for i in range(tentativas):
        r = requests.post(COMEXSTAT_URL, json=body, timeout=180)
        js = r.json() if r.content else {}
        if "data" in js:
            return js["data"]["list"]
        time.sleep(espera * (i + 1))  # limite de requisições: espera crescente
    raise RuntimeError(f"ComexStat falhou: {r.status_code} {r.text[:200]}")


def consulta_cache(nome: str, body: dict) -> list:
    arq = CACHE / f"{nome}.json"
    if arq.exists():
        return json.loads(arq.read_text(encoding="utf-8"))
    linhas = consulta(body)
    arq.write_text(json.dumps(linhas), encoding="utf-8")
    time.sleep(3)
    return linhas


def mensal_por_ano(ano_ini: int, ano_fim: int, filtro: str, valores: list, detalhe: str,
                   fluxo: str = "import", mes_fim_ultimo_ano: int = 12) -> list:
    """Uma requisição por ano (a API aplica o intervalo de meses a todos os anos do período)."""
    linhas = []
    for ano in range(ano_ini, ano_fim + 1):
        mes_fim = mes_fim_ultimo_ano if ano == ano_fim else 12
        body = {"flow": fluxo, "monthDetail": True,
                "period": {"from": f"{ano}-01", "to": f"{ano}-{mes_fim:02d}"},
                "filters": [{"filter": filtro, "values": valores}],
                "details": [detalhe], "metrics": ["metricFOB", "metricKG"]}
        linhas += consulta_cache(f"{fluxo}_{filtro}_{detalhe}_{ano}_{mes_fim:02d}", body)
        print(f"  {fluxo} {filtro} {ano}: ok", flush=True)
    return linhas
