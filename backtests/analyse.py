import sys, numpy as np, pandas as pd
OUT = sys.argv[1]
G = pd.read_csv(f"{OUT}/jeux.csv"); S = pd.read_csv(f"{OUT}/structurel.csv")
D = pd.read_csv(f"{OUT}/dca.csv"); T = pd.read_csv(f"{OUT}/trades.csv")

def brier(df):
    o = np.stack([(df.out == k).astype(float) for k in "ABC"], 1)
    pr = df[["pA", "pB", "pC"]].values
    return ((pr - o) ** 2).sum(1).mean()

print("=== 1. JEUX TACTIQUES 7 JOURS (processus réel avec ré-ancrage) ===")
print(f"Jeux : {len(G)}  du {G.date.iloc[0]} au {G.date.iloc[-1]}")
for k in "ABC":
    print(f"  {k} : prédit moyen {G['p'+k].mean()*100:.1f} %  réalisé {np.mean(G.out==k)*100:.1f} %")
# climatologie expansive (uniquement les jeux passés)
clim = []
for n in range(len(G)):
    past = G.out.iloc[:n]
    if n < 20: clim.append((1/3, 1/3, 1/3)); continue
    clim.append(tuple(np.mean(past == k) for k in "ABC"))
C = np.array(clim); o = np.stack([(G.out == k).astype(float) for k in "ABC"], 1)
print(f"Brier méthode {brier(G):.3f} | uniforme {((1/3 - o)**2).sum(1).mean():.3f} | climatologie passée {((C - o)**2).sum(1).mean():.3f}  (plus bas = mieux)")
print("Calibration par tranche (toutes classes confondues) :")
pr = G[["pA", "pB", "pC"]].values.ravel(); ob = o.ravel()
bins = [0, .1, .2, .3, .4, .5, .6, .7, .8, 1.01]
for a, b in zip(bins[:-1], bins[1:]):
    m = (pr >= a) & (pr < b)
    if m.sum() >= 10: print(f"  prédit {a:.1f}-{b:.1f}: n={m.sum():4d} prédit {pr[m].mean()*100:5.1f} % réalisé {ob[m].mean()*100:5.1f} %")
print("Par régime (prix vs SMA200) :")
for reg, g in G.groupby("regime"):
    print(f"  {reg:9s} n={len(g)}  B prédit {g.pB.mean()*100:.0f} % réalisé {np.mean(g.out=='B')*100:.0f} % | C prédit {g.pC.mean()*100:.0f} % réalisé {np.mean(g.out=='C')*100:.0f} % | Brier {brier(g):.3f}")
print("Par momentum 90 j :")
G["momb"] = pd.cut(G.mom90, [-9, -0.2, 0, 0.2, 9], labels=["<-20%", "-20-0%", "0-20%", ">20%"])
for b, g in G.groupby("momb", observed=True):
    print(f"  {b:7s} n={len(g)} B prédit {g.pB.mean()*100:.0f} % réalisé {np.mean(g.out=='B')*100:.0f} % | C prédit {g.pC.mean()*100:.0f} % réalisé {np.mean(g.out=='C')*100:.0f} %")
# persistance après résolution
G["prev"] = G.out.shift(1)
print("Après un jeu résolu :")
for k in "ABC":
    g = G[G.prev == k]
    print(f"  après {k} (n={len(g)}): B prédit {g.pB.mean()*100:.0f} % réalisé {np.mean(g.out=='B')*100:.0f} % | C prédit {g.pC.mean()*100:.0f} % réalisé {np.mean(g.out=='C')*100:.0f} %")
G["width"] = np.log(G.U / G.L) / (G.sig * np.sqrt(7))
print(f"Largeur de range en écarts-types hebdo : médiane {G.width.median():.2f}, 10e pct {G.width.quantile(.1):.2f}, 90e pct {G.width.quantile(.9):.2f}")
print(f"Jeux en choc (vol x1,25) : {G.shock.mean()*100:.0f} %")

print("\n=== 2. STRUCTUREL 4 SEMAINES (évaluation tous les 3 jours, chevauchante) ===")
for lv in (5, 10, 15):
    for side in ("up", "dn"):
        print(f"  toucher {'+' if side=='up' else '-'}{lv} % : prédit {S[f'p_{side}{lv}'].mean()*100:4.1f} % réalisé {S[f'o_{side}{lv}'].mean()*100:4.1f} %")
print(f"  intervalle 80 % : couverture réelle {S.in80.mean()*100:.1f} % (sous q10 {S.below10.mean()*100:.1f} %, au-dessus q90 {S.above90.mean()*100:.1f} %)")
for reg, g in S.groupby("regime"):
    print(f"  {reg:9s}: +10 % prédit {g.p_up10.mean()*100:.0f} réalisé {g.o_up10.mean()*100:.0f} | -10 % prédit {g.p_dn10.mean()*100:.0f} réalisé {g.o_dn10.mean()*100:.0f} | couverture 80 % : {g.in80.mean()*100:.0f}")

print("\n=== 3. DCA EN PALIERS vs ACHAT UNIQUE vs 4 ACHATS HEBDO (départ chaque semaine) ===")
D["vs_lump"] = D.ladder / D.lump - 1; D["vs_weekly"] = D.ladder / D.weekly - 1; D["weekly_vs_lump"] = D.weekly / D.lump - 1
print(f"n={len(D)}  coût moyen paliers vs achat unique : {D.vs_lump.mean()*100:+.2f} % (médiane {D.vs_lump.median()*100:+.2f} %, meilleur dans {np.mean(D.vs_lump<0)*100:.0f} % des cas)")
print(f"         paliers vs 4 achats hebdo : {D.vs_weekly.mean()*100:+.2f} % (meilleur dans {np.mean(D.vs_weekly<0)*100:.0f} % des cas)")
print(f"         4 achats hebdo vs unique : {D.weekly_vs_lump.mean()*100:+.2f} %")
for reg, g in D.groupby("regime"):
    print(f"  {reg:9s} n={len(g)} paliers vs unique {g.vs_lump.mean()*100:+.2f} % | vs hebdo {g.vs_weekly.mean()*100:+.2f} %")
print(f"  pire cas paliers vs unique : {D.vs_lump.max()*100:+.1f} % le {D.loc[D.vs_lump.idxmax(),'date']} ; meilleur : {D.vs_lump.min()*100:+.1f} % le {D.loc[D.vs_lump.idxmin(),'date']}")

print("\n=== 4. TRADE TACTIQUE (long bas de range, stop sous la borne, cibles milieu puis haut) ===")
f = T[T.filled]
print(f"Signaux {len(T)}, exécutés {len(f)} ({len(f)/len(T)*100:.0f} %) ; gain moyen {f.R.mean():+.2f} R ; gagnants {np.mean(f.R>0)*100:.0f} % ; total {f.R.sum():+.1f} R")
for reg, g in f.groupby("regime"):
    print(f"  {reg:9s} n={len(g)} gain moyen {g.R.mean():+.2f} R gagnants {np.mean(g.R>0)*100:.0f} %")
