import sys; sys.argv=['x', sys.argv[1] if len(sys.argv)>1 else '../data/btc_cm.csv']
exec(open('sorties.py').read())
import itertools
def windows(a,b,yrs=3,step=60):
    i=np.searchsorted(d,a); j=np.searchsorted(d,b); L=int(365.25*yrs); out=[]
    while i+L<=j: out.append((d[i],d[i+L])); i+=step
    return out
P={'train':windows('2016-01-01','2021-01-01'),'test':windows('2021-01-01','2026-05-23')}
base={k:[run(s,e) for s,e in w] for k,w in P.items()}
def score(rule,prm,k):
    r=[run(s,e,rule,prm) for s,e in P[k]]
    rat=np.array([a[0]/b[0] for a,b in zip(r,base[k])]); dd=np.array([a[1]-b[1] for a,b in zip(r,base[k])])
    return rat.mean()-1,(rat>1).mean(),dd.mean(),len(r)
grid=[]
for q,f,re,kk in itertools.product([0.85,0.9,0.95],[0.05,0.1,0.2],['acc','trend'],[4,12]):
    grid.append(('paliers',dict(q=q,f=f,re=re,k=kk)))
for D,s,re,kk in itertools.product([90,180,365],[0.5,1.0],['acc','trend'],[4,12]):
    grid.append(('tendance',dict(D=D,s=s,re=re,k=kk)))
for q,f,D,s,re in itertools.product([0.9,0.95],[0.05,0.1],[180,365],[0.5,1.0],['acc','trend']):
    grid.append(('combi',dict(q=q,f=f,D=D,s=s,re=re,k=12)))
res=[]
for rule,prm in grid:
    tr=score(rule,prm,'train'); te=score(rule,prm,'test'); res.append((rule,prm,tr,te))
json.dump([(a,b,c,dd) for a,b,c,dd in res],open('grille.json','w'))
print('fenetres',len(P['train']),len(P['test']))
for rule in ['paliers','tendance','combi']:
    rr=sorted([x for x in res if x[0]==rule],key=lambda x:-x[2][0])
    print('==',rule,'meilleur réglage sur 2016-2020 puis test 2021-2026')
    for x in rr[:3]: print('  ',x[1],'train %+.1f%% (mieux %.0f%%, DD %+.0f pts)'%(x[2][0]*100,x[2][1]*100,x[2][2]*100),'| test %+.1f%% (mieux %.0f%%, DD %+.0f pts)'%(x[3][0]*100,x[3][1]*100,x[3][2]*100))
    te=np.array([x[3][0] for x in rr]); print('   tous réglages en test : médiane %+.1f%%, part > 0 : %.0f%%'%(np.median(te)*100,(te>0).mean()*100))
