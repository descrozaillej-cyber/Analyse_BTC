import sys, numpy as np, pandas as pd
exec(open('bt/backtest_core.py').read())
G = pd.read_csv('out/jeux.csv')
# Correction de calibration de A estimée sur 2018-2022, testée 2023-2026
tr, te = G[G.date < '2023-01-01'], G[G.date >= '2023-01-01']
def brier(df, a=0.0):
    pA = np.clip(df.pA + a, 0, 1); sc = (1 - pA) / (df.pB + df.pC)
    pr = np.stack([pA, df.pB * sc, df.pC * sc], 1)
    o = np.stack([(df.out == k).astype(float) for k in "ABC"], 1)
    return ((pr - o) ** 2).sum(1).mean()
a = np.mean(tr.out == 'A') - tr.pA.mean()
print(f"Correction A estimée 2018-2022 : {a*100:+.1f} pts ; Brier test 2023-2026 sans {brier(te):.3f} avec {brier(te, a):.3f} ; A test prédit {te.pA.mean()*100:.0f} réalisé {np.mean(te.out=='A')*100:.0f}")
moments = [("2018-01-08","après le pic de déc. 2017, avant le marché baissier"),("2018-11-13","avant la chute 6,3k vers 3,2k"),
 ("2019-04-01","avant le rallye 2019"),("2019-06-26","pic 2019 à 13k"),("2020-03-11","veille du krach Covid"),
 ("2020-10-20","début du bull run 2020-21"),("2021-04-14","pic d'avril 2021"),("2021-05-11","avant le krach de mai 2021"),
 ("2021-11-10","plus haut historique 2021"),("2022-05-08","effondrement Luna"),("2022-11-07","faillite FTX"),
 ("2023-03-10","crise SVB, avant le rallye"),("2023-06-20","avant le range de l'été 2023"),("2024-03-14","plus haut pré-halving, avant 7 mois de range"),
 ("2024-11-05","élection américaine"),("2025-10-06","plus haut historique 126k")]
rows = []
for d, lab in moments:
    i = int(np.where(dates == d)[0][0])
    L, U, L2, U2 = bounds(i); (pA, pB, pC), sh = game_probs(i, L, U); sp = struct_probs(i)
    out = "A"
    for k in range(i + 1, i + 8):
        if p[k] > U: out = "B"; break
        if p[k] < L: out = "C"; break
    pred = max(zip((pA, pB, pC), "ABC"))[1]
    r28 = p[i+28]/p[i]-1; r90 = p[i+90]/p[i]-1 if i+90 < N else np.nan
    in80 = sp["q10"] <= p[i+28] <= sp["q90"]
    rows.append(dict(date=d, contexte=lab, prix=round(p[i]), L=round(L), U=round(U), A=round(pA*100), B=round(pB*100), C=round(pC*100),
        favori=pred, issue=out, ok=pred==out, r28=round(r28*100,1), dans80=in80, r90=round(r90*100,1), mvrv=round(mvrv[i],2), sma200="au-dessus" if p[i]>sma200[i] else "en dessous"))
M = pd.DataFrame(rows); pd.set_option('display.width', 250); pd.set_option('display.max_columns', 30)
print(M.to_string(index=False)); M.to_csv('out/moments.csv', index=False)
print(f"Favori juste : {M.ok.mean()*100:.0f} % ; issue 28 j dans l'intervalle 80 % : {M.dans80.mean()*100:.0f} %")
