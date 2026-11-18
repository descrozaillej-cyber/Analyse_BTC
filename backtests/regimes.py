"""Indicateurs de régime bull/bear. Paramètres standards fixés AVANT le test (pas de réglage).
Signal calculé à la clôture du jour t avec les données <= t, appliqué à partir de t+1.
"""
import sys, numpy as np, pandas as pd
df = pd.read_csv(sys.argv[1], usecols=["time", "PriceUSD", "CapMVRVCur", "HashRate"])
df = df.dropna(subset=["PriceUSD"]).reset_index(drop=True)
df["time"] = pd.to_datetime(df["time"]); df = df[df.time <= "2026-05-23"].reset_index(drop=True)
p = df.PriceUSD; d = df.time
sma50, sma200 = p.rolling(50).mean(), p.rolling(200).mean()
sma1400 = p.rolling(1400).mean()  # moyenne 200 semaines
mom365 = p / p.shift(365) - 1
mv = df.CapMVRVCur
rank = mv.rolling(4 * 365, min_periods=365).apply(lambda w: (w[:-1] < w[-1]).mean(), raw=True)
hr30, hr60 = df.HashRate.rolling(30).mean(), df.HashRate.rolling(60).mean()

sig = pd.DataFrame({"time": d})
sig["Prix > SMA200"] = (p > sma200)
sig["SMA50 > SMA200"] = (sma50 > sma200)
sig["Momentum 12 mois > 0"] = (mom365 > 0)
sig["Rang MVRV < 80 %"] = (rank < 0.8)
sig["Tendance OU valeur (prix > SMA200 ou rang MVRV < 20 %)"] = (p > sma200) | (rank < 0.2)
sig["Tendance ET pas cher (prix > SMA200 et rang MVRV < 80 %)"] = (p > sma200) & (rank < 0.8)

start = d.searchsorted(pd.Timestamp("2016-01-01"))
r = p.pct_change().fillna(0).values
FEE = 0.002  # 0,2 % par changement de position

def perf(pos, a, b):
    pos = pos.astype(float).values
    held = np.r_[0, pos[:-1]]  # signal de la veille
    ret = held[a:b] * r[a:b] - FEE * np.abs(np.diff(np.r_[held[a], held[a:b]]))
    eq = np.cumprod(1 + ret); yrs = (b - a) / 365
    dd = (eq / np.maximum.accumulate(eq) - 1).min()
    switches = int(np.abs(np.diff(held[a:b])).sum())
    return eq[-1] ** (1 / yrs) - 1, dd, held[a:b].mean(), switches, eq[-1]

periods = {"2016-2026": ("2016-01-01", "2026-05-23"), "2016-2019": ("2016-01-01", "2019-12-31"),
           "2020-2022": ("2020-01-01", "2022-12-31"), "2023-2026": ("2023-01-01", "2026-05-23")}
cols = ["Acheter et garder"] + list(sig.columns[1:])
for pname, (s, e) in periods.items():
    a, b = d.searchsorted(pd.Timestamp(s)), d.searchsorted(pd.Timestamp(e))
    print(f"\n=== {pname} ===  (rendement annuel | pire baisse | temps investi | changements | multiple)")
    for c in cols:
        pos = pd.Series(np.ones(len(p))) if c == "Acheter et garder" else sig[c]
        cg, dd, inv, sw, m = perf(pos, a, b)
        print(f"  {c:58s} {cg*100:+6.0f} % | {dd*100:5.0f} % | {inv*100:3.0f} % | {sw:3d} | x{m:.1f}")

# Retard aux retournements de cycle (points choisis après coup, uniquement pour mesurer le retard)
turns = {"creux déc. 2018": ("2018-12-15", "bull"), "creux mars 2020": ("2020-03-12", "bull"), "creux nov. 2022": ("2022-11-21", "bull"),
         "sommet déc. 2017": ("2017-12-17", "bear"), "sommet nov. 2021": ("2021-11-10", "bear"), "sommet oct. 2025": ("2025-10-06", "bear")}
print("\n=== Retard des signaux aux retournements (prix au moment du signal vs extrême) ===")
for c in ["Prix > SMA200", "SMA50 > SMA200", "Momentum 12 mois > 0", "Tendance OU valeur (prix > SMA200 ou rang MVRV < 20 %)"]:
    out = []
    for name, (td, kind) in turns.items():
        i = d.searchsorted(pd.Timestamp(td)); s_ = sig[c].values
        if kind == "bull":
            k = next((j for j in range(i, len(p)) if s_[j]), None)
        else:
            k = next((j for j in range(i, len(p)) if not s_[j]), None)
        if k is None: out.append(f"{name}: pas de signal"); continue
        out.append(f"{name}: {k-i} j, {(p[k]/p[i]-1)*100:+.0f} %")
    print(f"  {c}\n    " + " ; ".join(out))

# Rendements futurs selon l'état du signal (toutes dates 2016-2026)
print("\n=== Rendement à 180 jours selon l'état (médiane, part positive) ===")
fwd = p.shift(-180) / p - 1
m = (d >= "2016-01-01") & fwd.notna()
print(f"  Toutes dates : médiane {fwd[m].median()*100:+.0f} %, positif {np.mean(fwd[m]>0)*100:.0f} %")
for c in sig.columns[1:5]:
    on = m & sig[c]; off = m & ~sig[c]
    print(f"  {c:24s} vrai : {fwd[on].median()*100:+5.0f} % ({np.mean(fwd[on]>0)*100:.0f} % positif) | faux : {fwd[off].median()*100:+5.0f} % ({np.mean(fwd[off]>0)*100:.0f} % positif)")
cheap = m & (rank < 0.2); dear = m & (rank > 0.8)
print(f"  Rang MVRV < 20 % : {fwd[cheap].median()*100:+.0f} % ({np.mean(fwd[cheap]>0)*100:.0f} % positif) | rang > 80 % : {fwd[dear].median()*100:+.0f} % ({np.mean(fwd[dear]>0)*100:.0f} % positif)")
# Hash ribbons : achat quand la moyenne 30 j du hashrate repasse au-dessus de la 60 j après une capitulation
cross = (hr30 > hr60) & (hr30.shift(1) <= hr60.shift(1)) & (d >= "2016-01-01")
idx = [i for i in np.where(cross)[0] if i + 180 < len(p)]
f180 = [p[i + 180] / p[i] - 1 for i in idx]
print(f"\n=== Hash ribbons (fin de capitulation des mineurs) : {len(idx)} signaux, rendement 180 j médian {np.median(f180)*100:+.0f} %, positif {np.mean(np.array(f180)>0)*100:.0f} %")
