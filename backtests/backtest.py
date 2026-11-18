"""Backtest mécanique du cadre BTC_v3, sans biais d'anticipation.

Règle d'or : pour une date d'analyse i, tous les calculs utilisent uniquement p[:i+1].
Les données futures (p[i+1:]) servent seulement à constater le résultat.
"""
import sys, json
import numpy as np, pandas as pd

CSV = sys.argv[1]
OUT = sys.argv[2]
df = pd.read_csv(CSV, usecols=["time", "PriceUSD", "CapMVRVCur"])
df = df.dropna(subset=["PriceUSD"]).reset_index(drop=True)
df["time"] = pd.to_datetime(df["time"])
dates = df["time"].dt.strftime("%Y-%m-%d").values
p = df["PriceUSD"].values.astype(float)
mvrv = df["CapMVRVCur"].values.astype(float)
N = len(p)
r = np.zeros(N); r[1:] = np.diff(np.log(p))

# Indicateurs causaux (valeur au jour i n'utilise que <= i)
sig30 = pd.Series(r).rolling(30).std(ddof=1).values
sma200 = pd.Series(p).rolling(200).mean().values
ema200 = pd.Series(p).ewm(span=200, adjust=False).mean().values
W = 7  # pivot confirmé W jours après
piv = []  # (jour du pivot, prix)
for j in range(W, N - W):
    win = p[j - W:j + W + 1]
    if p[j] == win.max() or p[j] == win.min():
        piv.append((j, p[j]))
piv_days = np.array([a for a, _ in piv]); piv_px = np.array([b for _, b in piv])

rng = np.random.default_rng(42)
NP = 8000
Z7 = rng.standard_normal((NP, 7)); Z28 = rng.standard_normal((NP, 28))

def candidates(i):
    m = (piv_days <= i - W) & (piv_days >= i - 365)  # pivots confirmés et passés seulement
    c = list(piv_px[m]) + [sma200[i], ema200[i]]
    return np.array([x for x in c if np.isfinite(x)])

def bounds(i):
    P = p[i]; s = sig30[i] * np.sqrt(7)
    c = candidates(i)
    dmin = 0.8 * s
    below = c[c <= P * np.exp(-dmin)]; above = c[c >= P * np.exp(dmin)]
    L = below.max() if len(below) and below.max() >= P * np.exp(-3 * s) else P * np.exp(-1.5 * s)
    U = above.min() if len(above) and above.min() <= P * np.exp(3 * s) else P * np.exp(1.5 * s)
    below2 = c[c <= L * np.exp(-0.5 * s)]; above2 = c[c >= U * np.exp(0.5 * s)]
    L2 = below2.max() if len(below2) and below2.max() >= L * np.exp(-3 * s) else L * np.exp(-s)
    U2 = above2.min() if len(above2) and above2.min() <= U * np.exp(3 * s) else U * np.exp(s)
    return L, U, L2, U2

def game_probs(i, L, U):
    P = p[i]; s = sig30[i]
    shock = abs(r[i]) > 2 * s
    out = []
    for k in ([1.0, 1.25] if shock else [1.0]):
        paths = P * np.exp(np.cumsum(Z7 * s * k, axis=1))
        up = paths > U; dn = paths < L
        fu = np.where(up.any(1), up.argmax(1), 99); fd = np.where(dn.any(1), dn.argmax(1), 99)
        B = np.mean(fu < fd); C = np.mean(fd < fu); out.append((1 - B - C, B, C))
    return tuple(np.mean(out, axis=0)), shock

def struct_probs(i):
    P = p[i]; s = sig30[i]
    paths = P * np.exp(np.cumsum(Z28 * s, axis=1))
    mx = paths.max(1); mn = paths.min(1)
    res = {}
    for lv in (0.05, 0.10, 0.15):
        res[f"up{int(lv*100)}"] = np.mean(mx >= P * (1 + lv))
        res[f"dn{int(lv*100)}"] = np.mean(mn <= P * (1 - lv))
    res["q10"], res["q90"] = np.quantile(paths[:, -1], [0.1, 0.9])
    return res

start = int(np.where(dates == "2018-01-01")[0][0])
end = N - 29  # il faut 28 jours de futur pour constater

# 1) Processus réel : jeux successifs avec ré-ancrage (pas de chevauchement)
games = []
i = start
while i + 7 < end:
    L, U, L2, U2 = bounds(i)
    (pA, pB, pC), shock = game_probs(i, L, U)
    outcome, j = "A", i + 7
    for d in range(i + 1, i + 8):  # constat avec les relevés futurs
        if p[d] > U: outcome, j = "B", d; break
        if p[d] < L: outcome, j = "C", d; break
    reg = "haussier" if p[i] > sma200[i] else "baissier"
    games.append(dict(date=dates[i], P=p[i], L=L, U=U, L2=L2, U2=U2, pA=pA, pB=pB, pC=pC,
                      shock=bool(shock), out=outcome, end=dates[j], regime=reg, mvrv=mvrv[i],
                      sig=sig30[i], mom90=p[i] / p[i - 90] - 1))
    i = j
G = pd.DataFrame(games)
G.to_csv(f"{OUT}/jeux.csv", index=False)

# 2) Évaluation quotidienne (chevauchante) du structurel 4 semaines
rows = []
for i in range(start, end):
    sp = struct_probs(i) if (i - start) % 3 == 0 else None
    if sp is None: continue
    fut = p[i + 1:i + 29]
    row = dict(date=dates[i], regime="haussier" if p[i] > sma200[i] else "baissier")
    for lv in (0.05, 0.10, 0.15):
        row[f"p_up{int(lv*100)}"] = sp[f"up{int(lv*100)}"]; row[f"o_up{int(lv*100)}"] = float(fut.max() >= p[i] * (1 + lv))
        row[f"p_dn{int(lv*100)}"] = sp[f"dn{int(lv*100)}"]; row[f"o_dn{int(lv*100)}"] = float(fut.min() <= p[i] * (1 - lv))
    row["in80"] = float(sp["q10"] <= p[i + 28] <= sp["q90"])
    row["below10"] = float(p[i + 28] < sp["q10"]); row["above90"] = float(p[i + 28] > sp["q90"])
    rows.append(row)
S = pd.DataFrame(rows); S.to_csv(f"{OUT}/structurel.csv", index=False)

# 3) Recommandation DCA en paliers vs achat unique vs 4 achats hebdo, départ chaque semaine
dca = []
for i in range(start, end, 7):
    L, U, L2, U2 = bounds(i)
    fut = p[i + 1:i + 29]
    cost_units = [(1/3) / p[i]]  # palier 1 au prix du jour
    t2 = t3 = False; done = False
    for d, px in enumerate(fut, start=1):
        if not t2 and px <= L: cost_units.append((1/3) / px); t2 = True
        if t2 and not t3 and px <= L2: cost_units.append((1/3) / px); t3 = True
        if not t2 and px > U:  # rebond sans avoir touché L : reste investi
            cost_units.append((2/3) / px); done = True; break
        if t2 and t3: done = True; break
    if not done:
        rest = 1 - (1/3) - (1/3) * t2 - (1/3) * t3
        cost_units.append(rest / p[i + 28])
    avg_ladder = 1 / sum(cost_units)
    avg_weekly = 4 / sum(1 / p[i + k] for k in (0, 7, 14, 21))
    dca.append(dict(date=dates[i], lump=p[i], ladder=avg_ladder, weekly=avg_weekly,
                    regime="haussier" if p[i] > sma200[i] else "baissier", mvrv=mvrv[i]))
D = pd.DataFrame(dca); D.to_csv(f"{OUT}/dca.csv", index=False)

# 4) Trade tactique à blanc : achat limite près du bas de range, stop dessous, cibles milieu puis haut
tr = []
for g in games:
    i = int(np.where(dates == g["date"])[0][0])
    L, U = g["L"], g["U"]
    entry, stop, t1, t2 = L * 1.01, L * 0.975, g["P"], U
    if not (stop < entry < t1 < t2): continue
    fill = None
    for d in range(i + 1, min(i + 8, N)):
        if p[d] <= entry: fill = d; break
    if fill is None:
        tr.append(dict(date=g["date"], filled=False, R=0.0, regime=g["regime"])); continue
    risk = entry - stop; half = 0; R = 0.0; exit_d = None
    for d in range(fill, min(fill + 22, N)):
        px = p[d]
        if px <= stop: R += (1 - half) * (px - entry) / risk; exit_d = d; break
        if half == 0 and px >= t1: R += 0.5 * (t1 - entry) / risk; half = 0.5
        if half == 0.5 and px >= t2: R += 0.5 * (t2 - entry) / risk; exit_d = d; half = 1; break
    if exit_d is None:
        last = min(fill + 21, N - 1); R += (1 - half) * (p[last] - entry) / risk
    tr.append(dict(date=g["date"], filled=True, R=R, regime=g["regime"]))
T = pd.DataFrame(tr); T.to_csv(f"{OUT}/trades.csv", index=False)
print("ok", len(G), len(S), len(D), len(T), dates[start], dates[end])
