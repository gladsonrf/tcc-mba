"""Executa todo o pipeline de dados em ordem."""
import subprocess
import sys
from pathlib import Path

PASTA = Path(__file__).parent
for script in ["01_baixar_comexstat.py", "02_baixar_pinksheet.py", "03_baixar_gpr.py",
               "04_baixar_bcb.py", "05_montar_base.py", "06_exportacoes_agro.py", "07_planilha_culturas.py",
               "08_gpr_ponderado.py"]:
    print(f"\n=== {script} ===")
    subprocess.run([sys.executable, str(PASTA / script)], check=True, cwd=PASTA)
