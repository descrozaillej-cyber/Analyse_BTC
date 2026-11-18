"""Trading de range, long seulement (acheter en bas, revendre en haut), sur clôtures quotidiennes.
Paramètres standards fixés AVANT le test : Bollinger 20 j / 2 écarts-types ; efficiency ratio (Kaufman) sur 30 j,
régime de range si ER < 0,25. Signal à la clôture de t, exécution à la clôture de t (approximation), rien du futur.
"""
import sys, numpy as np, pandas as pd
df = pd.read_csv(sys.argv[1], usecols=["time", "PriceUSD"]).dropna()
df["time"] = pd.to_datetime(df.time); df = df[df.time <= "2026-05-23"].reset_index(drop=True)
p = df.PriceUSD.values; d = df.time.dt.strftime("%Y-%m-%d").values; N = len(p)
s = pd.Series(p)
mid = s.rolling(20).mean().values; sd = s.rolling(20).std(ddof=0).values
low, up = mid - 2 * sd, mid + 2 * sd
er = (s.diff(30).abs() / s.diff().abs().rolling(30).sum()).values
FEE = 0.002  # aller-retour 0,2 %

def run(a, b, cond, exit_rule):
    trades = []; i = a
    while i < b - 1:
        if p[i] < low[i] and cond(i):
            entry = p[i]; stop = entry - (mid[i] - low[i])  # risque = demi-largeur de bande
            risk = entry - stop; out = None
            for j in range(i + 1, min(i + 21, N)):
                tgt = mid[j] if exit_rule == "milieu" else up[j]
                if p[j] <= stop: out = (j, p[j]); break
                if p[j] >= tgt: out = (j, p[j]); break
            if out is None: j = min(i + 20, N - 1); out = (j, p[j])
            ret = out[1] / entry - 1 - FEE
            trades.append(dict(date=d[i], ret=ret, R=(out[1] - entry) / risk, jours=out[0] - i))
            i = out[0] + 1
        else:
            i += 1
    return pd.DataFrame(trades)

def report(label, t):
    if len(t) == 0: print(f"  {label:44s} aucun trade"); return
    eq = np.prod(1 + t.ret.values) - 1
    print(f"  {label:44s} n={len(t):3d} gagnants {np.mean(t.ret>0)*100:3.0f} % | gain moyen {t.ret.mean()*100:+5.2f} % | médian {t.ret.median()*100:+5.2f} % | cumul {eq*100:+6.0f} % | durée {t.jours.mean():.0f} j")

always = lambda i: True
in_range = lambda i: er[i] < 0.25
trend = lambda i: er[i] >= 0.25
for per, (a_, b_) in {"2016-2020 (référence)": ("2016-01-01", "2020-12-31"), "2021-2026 (contrôle)": ("2021-01-01", "2026-05-23"), "2016-2026": ("2016-01-01", "2026-05-23")}.items():
    a, b = np.searchsorted(d, a_), np.searchsorted(d, b_)
    print(f"\n=== {per} ===")
    for ex in ("milieu", "haut"):
        report(f"tous régimes, sortie {ex} de bande", run(a, b, always, ex))
        report(f"range seulement (ER<0,25), sortie {ex}", run(a, b, in_range, ex))
        report(f"tendance seulement (ER>=0,25), sortie {ex}", run(a, b, trend, ex))

print("\n=== Mars à mai 2025 ===")
a, b = np.searchsorted(d, "2025-03-01"), np.searchsorted(d, "2025-05-31")
print(f"  prix : {p[a]:.0f} au 01/03, plus bas {p[a:b].min():.0f}, plus haut {p[a:b].max():.0f}, {p[b]:.0f} au 31/05")
print(f"  jours en régime de range (ER<0,25) : {np.mean(er[a:b]<0.25)*100:.0f} %")
for ex in ("milieu", "haut"):
    t = run(a, b, in_range, ex); print(f"  sortie {ex}:"); print(t.to_string(index=False) if len(t) else "  aucun trade")
