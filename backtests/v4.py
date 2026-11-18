"""Backtest v4 : (1) DCA hebdomadaire modulé par le MVRV ; (2) asymétrie structurelle 4 semaines.
Anti-triche : chaque décision à la date i n'utilise que les données <= i. Les seuils "appris"
le sont sur la période d'entraînement et évalués sur la période de test.
"""
import sys, numpy as np, pandas as pd
sys.argv = ["x", sys.argv[1], sys.argv[2]]
exec(open(__file__.replace("v4.py", "backtest_core.py")).read())
mv = pd.Series(mvrv)
last = int(np.where(~np.isnan(mvrv))[0].max())  # dernière date avec MVRV

# Percentile causal du MVRV sur les 4 années passées (fenêtre glissante, données <= i)
pct = mv.rolling(4 * 365, min_periods=365).apply(lambda w: (w[:-1] < w[-1]).mean(), raw=True).values

def mult(i, rule):
    m = mvrv[i]
    if rule == "constant": return 1.0
    if rule == "seuils 1 / 2,5":   # seuils observés sur tout l'échantillon (risque de sur-ajustement)
        return 1.5 if m < 1 else (0.5 if m > 2.5 else 1.0)
    if rule == "seuils 1 / 3,5":   # seuils de la littérature MVRV (2018), fixés a priori
        return 1.5 if m < 1 else (0.5 if m > 3.5 else 1.0)
    if rule == "percentile 20/80":  # sans seuil choisi : rang du MVRV dans ses 4 dernières années
        q = pct[i]
        return 1.0 if np.isnan(q) else (1.5 if q < 0.2 else (0.5 if q > 0.8 else 1.0))

rules = ["constant", "seuils 1 / 2,5", "seuils 1 / 3,5", "percentile 20/80"]
i0 = int(np.where(dates == "2018-01-01")[0][0])
H = 104 * 7  # fenêtre de 2 ans d'achats hebdomadaires
rows = []
for s in range(i0, last - H, 30):
    days = range(s, s + H, 7)
    endv = p[s + H]
    res = {"start": dates[s]}
    for rule in rules:
        amt = np.array([mult(d, rule) for d in days]); px = p[list(days)]
        btc = (amt / px).sum(); inv = amt.sum()
        res[rule] = dict(cost=inv / btc, inv=inv, mult=btc * endv / inv)
    rows.append(res)

def summary(sel, label):
    print(f"\n{label} : {len(sel)} fenêtres de 2 ans")
    base = np.array([r["constant"]["cost"] for r in sel])
    for rule in rules[1:]:
        c = np.array([r[rule]["cost"] for r in sel]); inv = np.array([r[rule]["inv"] for r in sel])
        rel = c / base - 1
        mtp = np.array([r[rule]["mult"] for r in sel]); mtp0 = np.array([r["constant"]["mult"] for r in sel])
        print(f"  {rule:18s} coût moyen par BTC vs constant {rel.mean()*100:+.1f} % (meilleur {np.mean(rel<0)*100:.0f} % des fenêtres, pire {rel.max()*100:+.1f} %) | montant investi {inv.mean()/104*100:.0f} % du constant | multiple final {mtp.mean():.2f} vs {mtp0.mean():.2f}")

summary(rows, "Toutes fenêtres (début 2018 à 2024)")
summary([r for r in rows if r["start"] < "2021-01-01"], "Fenêtres débutant 2018-2020")
summary([r for r in rows if r["start"] >= "2021-01-01"], "Fenêtres débutant 2021-2024 (hors échantillon pour la règle à seuils 1/2,5 ? non : seuils vus sur tout l'échantillon)")

# (2) Asymétrie structurelle : dérive conditionnelle au MVRV, apprise 2018-2021, testée 2022-2026
buckets = [0, 1, 1.5, 2, 2.5, 99]
def bucket(m): return int(np.digitize(m, buckets)) - 1
train = [i for i in range(i0, N - 29) if dates[i] < "2022-01-01" and not np.isnan(mvrv[i])]
test = [i for i in range(i0, N - 29) if dates[i] >= "2022-01-01" and not np.isnan(mvrv[i]) and i <= last]
mu = {}
for b in range(5):
    lr = [np.log(p[i + 28] / p[i]) / 28 for i in train if bucket(mvrv[i]) == b]
    mu[b] = (np.mean(lr) if len(lr) > 30 else 0.0, len(lr))
print("\nDérive quotidienne apprise 2018-2021 par tranche de MVRV :", {f"{buckets[b]}-{buckets[b+1]}": (round(v[0]*100, 3), v[1]) for b, v in mu.items()})
# facteur de queue : volatilité x k pour couvrir 80 % sur l'entraînement
def preds(i, drift, k):
    s = sig30[i] * k
    paths = p[i] * np.exp(np.cumsum(Z28 * s + drift - 0.5 * s * s * 0, axis=1))
    return (np.mean(paths.max(1) >= p[i] * 1.10), np.mean(paths.min(1) <= p[i] * 0.90), *np.quantile(paths[:, -1], [0.1, 0.9]))
def evaluate(idx, use_drift, k, shrink=1.0):
    bu = bd = cov = 0.0; n = 0
    for i in idx[::3]:
        d = shrink * mu[bucket(mvrv[i])][0] if use_drift else 0.0
        pu, pd_, q10, q90 = preds(i, d, k)
        ou = float(p[i + 1:i + 29].max() >= p[i] * 1.1); od = float(p[i + 1:i + 29].min() <= p[i] * 0.9)
        bu += (pu - ou) ** 2; bd += (pd_ - od) ** 2; cov += float(q10 <= p[i + 28] <= q90); n += 1
    return bu / n, bd / n, cov / n
best_k = min([1.0, 1.1, 1.2, 1.3], key=lambda k: abs(evaluate(train, False, k)[2] - 0.8))
print(f"Facteur de queue retenu sur 2018-2021 : x{best_k}")
for label, use_d, k, sh in [("v3 (sans dérive, x1)", False, 1.0, 1.0), ("queue seule", False, best_k, 1.0),
                            ("dérive MVRV", True, 1.0, 1.0), ("dérive MVRV réduite de moitié + queue", True, best_k, 0.5)]:
    tr_ = evaluate(train, use_d, k, sh); te_ = evaluate(test, use_d, k, sh)
    print(f"  {label:38s} entraînement Brier +10 % {tr_[0]:.3f} -10 % {tr_[1]:.3f} couverture {tr_[2]*100:.0f} % | test 2022-26 Brier +10 % {te_[0]:.3f} -10 % {te_[1]:.3f} couverture {te_[2]*100:.0f} %")
