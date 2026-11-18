#!/usr/bin/env python3
"""Vérifie btc_calc.py sur des valeurs connues (clôtures Crypto.com BTC_USDT du 25/09 au 12/11/2026).
Valeurs de référence : bilan de test v5 du 13/11/2026 (ER 0,369 ; Bollinger 71 982,52 / 77 333,08 / 82 683,64).
Usage : python3 selftest.py  (sortie "OK" ou la liste des écarts)
"""
import json, os, subprocess, sys, tempfile

CLOSES = [84103.13, 84435.10, 84480.58, 83497.82, 83657.79, 83621.59, 84876.20, 84519.00, 84763.62, 86519.99,
          85757.01, 85544.27, 83325.35, 81747.82, 82624.26, 82984.89, 83764.37, 81837.78, 83180.66, 81677.16,
          82228.21, 81611.01, 81494.61, 82107.18, 81943.99, 83027.36, 84101.96, 81425.99, 81190.05, 80877.00,
          80148.00, 80143.58, 80906.28, 81351.41, 77976.96, 77314.18, 77530.55, 78346.24, 76807.53, 77452.93,
          80512.26, 76093.97, 75848.19, 75872.99, 74854.99, 75361.37, 73793.96, 74009.22, 71459.99]

inp = {"closes": CLOSES, "price": 69071.96, "sma200": 73080.97, "mvrv": 1.33,
       "mvrv_p20": 1.234, "mvrv_p80": 2.219, "game_low": 65000, "game_high": 72000,
       "levels": [74000, 65000], "n": 50000}
here = os.path.dirname(os.path.abspath(__file__))
with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
    json.dump(inp, f)
out = json.loads(subprocess.check_output([sys.executable, os.path.join(here, "btc_calc.py"), f.name]))

errors = []
def check(name, got, want, tol):
    if abs(got - want) > tol:
        errors.append(f"{name}: obtenu {got:.4f}, attendu {want} (tolérance {tol})")

r = out["range"]
check("efficiency ratio", r["efficiency_ratio_30j"], 0.369, 0.002)
check("bande basse", r["bande_basse"], 71982.52, 1.0)
check("sma20", r["sma20"], 77333.08, 1.0)
check("bande haute", r["bande_haute"], 82683.64, 1.0)
if r["signal_entree"]:
    errors.append("signal de range attendu : non (ER au-dessus de 0,25)")
if out["regime"]["nom"] != "Prudence" or out["regime"]["multiplicateur_dca"] != 0.5:
    errors.append(f"régime attendu Prudence x0,5, obtenu {out['regime']}")
g = out["jeu_7j"]["base"]
if abs(sum(g.values()) - 1) > 1e-9:
    errors.append("probabilités du jeu ne totalisent pas 100 %")
check("proba A (ordre de grandeur, base 46 % au 13/11)", g["A"], 0.46, 0.08)
# Pi Cycle : série synthétique de 120 points sur 365 jours. Plate à 100 puis hausse sur les 60 derniers
# points : MM111 = moyenne des 37 derniers points, MM350 = moyenne des 115 derniers.
import numpy as np
v = [100.0] * 60 + list(np.linspace(100, 600, 60))
pi_in = dict(inp, n=2000, serie_365j={"startTs": 0, "endTs": 364 * 86400000, "prices": v})
with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
    json.dump(pi_in, f)
pc = json.loads(subprocess.check_output([sys.executable, os.path.join(here, "btc_calc.py"), f.name]))["pi_cycle"]
age = np.linspace(364, 0, 120); a = np.array(v)
want = a[age < 111].mean() / (2 * a[age < 350].mean())
check("ratio Pi Cycle", pc["ratio"], want, 1e-9)
if pc["alarme"] != (want >= 1):
    errors.append("alarme Pi Cycle incohérente avec le ratio")
print("OK" if not errors else "\n".join(errors))
sys.exit(1 if errors else 0)
