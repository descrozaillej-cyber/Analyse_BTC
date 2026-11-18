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

