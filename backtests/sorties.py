"""Backtest de règles de sortie BTC. Décision sur les données du jour i, exécution à la clôture i+1.
DCA hebdomadaire selon le régime (cadre v5), apports non investis exclus (mesure par euro investi).
"""
import numpy as np, pandas as pd, itertools, json, sys
df=pd.read_csv(sys.argv[1],usecols=['time','PriceUSD','CapMVRVCur']).dropna(subset=['PriceUSD'])
df['time']=pd.to_datetime(df.time); df=df.reset_index(drop=True)
p=df.PriceUSD.values; d=df.time.dt.strftime('%Y-%m-%d').values; N=len(p)
sma=pd.Series(p).rolling(200).mean().values
rank=df.CapMVRVCur.rolling(1460,min_periods=365).apply(lambda w:(w[:-1]<w[-1]).mean(),raw=True).values
FEE=0.001
def reg(i):
    q=rank[i]
    if np.isnan(q) or np.isnan(sma[i]): return 1.0,'n'
    if q<0.2: return 1.5,'acc'
    if q>0.8: return 0.5,'eup'
    return (1.0,'bull') if p[i]>sma[i] else (0.5,'pru')

def run(start,end,rule=None,prm=None):
    i0=np.searchsorted(d,start); i1=np.searchsorted(d,end)
    btc=cash=inv=0.0; hist=[]; last_eup=-10**9; exited=False; redeploy=0; sells=[]
    for i in range(i0,i1-1,7):
        m,r=reg(i); x=i+1; px=p[x]
        if r=='eup': last_eup=i
        inv+=m; btc+=m*(1-FEE)/px
        if rule:
            sell=0.0
            if rule in('paliers','combi') and rank[i]>prm['q']:
                sell=max(sell,prm['f'])
            if rule in('tendance','combi') and not exited and i-last_eup<=prm['D'] and p[i]<sma[i]:
                sell=max(sell,prm['s']); exited=True
            if r=='eup': exited=False
            if sell>0 and btc>0:
                q=btc*sell; btc-=q; cash+=q*px*(1-FEE); sells.append((d[x],px,q))
            # rachat
            reentry = (r=='acc') if prm['re']=='acc' else (p[i]>sma[i] and r!='eup')
            if cash>0 and reentry:
                if redeploy==0: redeploy=prm['k']; chunk0=cash/prm['k']
                amt=min(cash,cash/redeploy); btc+=amt*(1-FEE)/px; cash-=amt; redeploy=max(redeploy-1,1)
            elif not reentry: redeploy=0
        hist.append(btc*px+cash)
    v=btc*p[i1-1]+cash; h=np.array(hist); dd=float(np.max(1-h/np.maximum.accumulate(h)))
    return v/inv, dd, sells
