"""Variantes de la méthode : volatilité, tendance après résolution. Calibrées sur 2018-2022, testées sur 2023-2026."""
import sys, numpy as np, pandas as pd
sys.argv = [sys.argv[0], sys.argv[1], sys.argv[2]]
exec(open(__file__.replace("variantes.py", "backtest_core.py")).read())

def run(sigfun, shock_on=True):
    games = []; i = start
    while i + 7 < end:
        L, U, L2, U2 = bounds(i)
        P = p[i]; s = sigfun(i); shock = shock_on and abs(r[i]) > 2 * sig30[i]
        out = []
        for k in ([1.0, 1.25] if shock else [1.0]):
            paths = P * np.exp(np.cumsum(Z7 * s * k, axis=1))
            up = paths > U; dn = paths < L
            fu = np.where(up.any(1), up.argmax(1), 99); fd = np.where(dn.any(1), dn.argmax(1), 99)
            B = np.mean(fu < fd); C = np.mean(fd < fu); out.append((1 - B - C, B, C))
        pA, pB, pC = np.mean(out, axis=0)
        outcome, j = "A", i + 7
        for d in range(i + 1, i + 8):
            if p[d] > U: outcome, j = "B", d; break
            if p[d] < L: outcome, j = "C", d; break
        games.append(dict(date=dates[i], pA=pA, pB=pB, pC=pC, out=outcome))
        i = j
    return pd.DataFrame(games)

def brier(df):
    o = np.stack([(df.out == k).astype(float) for k in "ABC"], 1)
    return ((df[["pA", "pB", "pC"]].values - o) ** 2).sum(1).mean()

sig90 = pd.Series(r).rolling(90).std(ddof=1).values
sig365 = pd.Series(r).rolling(365).std(ddof=1).values
variants = {
    "v3 (vol 30 j + choc x1,25)": (lambda i: sig30[i], True),
    "vol 30 j sans choc": (lambda i: sig30[i], False),
    "vol 90 j": (lambda i: sig90[i], False),
    "moyenne vol 30 j et 365 j": (lambda i: 0.5 * (sig30[i] + sig365[i]), False),
}
res = {}
for name, (f, sh) in variants.items():
    g = run(f, sh); g["prev"] = g.out.shift(1); res[name] = g
    tr = g[g.date < "2023-01-01"]; te = g[g.date >= "2023-01-01"]
    print(f"{name:30s} Brier entraînement {brier(tr):.3f} test {brier(te):.3f} | A prédit {g.pA.mean()*100:.0f} réalisé {np.mean(g.out=='A')*100:.0f}")

# Correction de tendance après résolution, estimée sur 2018-2022 uniquement
print("\nCorrection de persistance (estimée sur 2018-2022, appliquée en 2023-2026) :")
for name in variants:
    g = res[name].copy(); tr = g[g.date < "2023-01-01"]
    fac = {}
    for prev in "BC":
        t = tr[tr.prev == prev]
        fac[prev] = {k: np.mean(t.out == k) / t["p" + k].mean() for k in "BC"}
    def adj(row):
        pA, pB, pC = row.pA, row.pB, row.pC
        if row.prev in fac:
            pB *= fac[row.prev]["B"]; pC *= fac[row.prev]["C"]; pA = max(0.0, 1 - pB - pC)
            s = pA + pB + pC; pA, pB, pC = pA / s, pB / s, pC / s
        return pd.Series(dict(pA=pA, pB=pB, pC=pC))
    adjd = g.apply(adj, axis=1); g2 = g.copy(); g2[["pA", "pB", "pC"]] = adjd
    te, te2 = g[g.date >= "2023-01-01"], g2[g2.date >= "2023-01-01"]
    sub = te.prev.isin(["B", "C"])
    print(f"  {name:30s} facteurs {{après B: B x{fac['B']['B']:.2f} C x{fac['B']['C']:.2f}; après C: B x{fac['C']['B']:.2f} C x{fac['C']['C']:.2f}}}")
    print(f"  {'':30s} test 2023-2026 : Brier sans {brier(te):.3f} avec {brier(te2):.3f} ; jeux après B ou C seulement : sans {brier(te[sub]):.3f} avec {brier(te2[sub]):.3f} (n={sub.sum()})")
