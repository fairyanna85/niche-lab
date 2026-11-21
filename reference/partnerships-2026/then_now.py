import json, math, re, collections, numpy as np
from scipy.stats import fisher_exact, norm, mannwhitneyu
from data import R, CODES
from hist import H
LABEL = dict(src="Owns partner-sourced pipeline/revenue", infl="Partner-influenced revenue", quota="Carries a quota / revenue number",
 arrn="Numeric ARR threshold", fcst="Forecasting / attribution", hyp="Hyperscalers (AWS/GCP/Azure)", gsi="GSIs / SIs / consultancies",
 isv="ISV / technology / integration partners", agy="Agencies", resl="Resellers / VARs / channel", mkt="Cloud marketplaces", cos="Co-sell",
 res="Resale", oem="OEM / embedded", com="Co-marketing / partner funds", prog="Partner program design", deal="Structures complex deals",
 aip="Employer sells AI", aiu="Candidate must use AI", aib="Candidate builds AI agents", aig="AI governance", tech="Technical depth",
 mgr="Manages people", pc="Player-coach / hands-on", zero="Build from zero", csuite="Reports to C-level", jbp="JBP / QBR / account mapping",
 tool="Named tools", agyb="Agency background valued", conb="Consulting background valued", hypb="Hyperscaler experience required",
 stb="Startup / high-growth experience", exec="C-level relationships", intl="International scope", lang="Languages required")
def p(r,k): return 1 if r["c"][k]>=1 else 0
def wilson(k,n,z=1.96):
    if n==0: return (0,0,0)
    ph=k/n; d=1+z*z/n; c=(ph+z*z/(2*n))/d; h=z*math.sqrt(ph*(1-ph)/n+z*z/(4*n*n))/d
    return ph, max(0,c-h), min(1,c+h)
E1=[h for h in H if h["era"]=="2020-21"]; E2=[h for h in H if h["era"]=="2024-25"]
BASE=H; NOWN=[r for r in R if r["city"]=="NYC"]; NOWA=R
def cochran_armitage(groups,k):
    # groups: list of lists in time order, scores 0,1,2
    ns=np.array([len(g) for g in groups]); xs=np.array([sum(p(r,k) for r in g) for g in groups]); t=np.arange(len(groups))
    N=ns.sum(); P=xs.sum()/N
    if P in (0,1): return 0.0,1.0
    T=np.sum(t*(xs-ns*P)); V=P*(1-P)*(np.sum(ns*t*t)-np.sum(ns*t)**2/N)
    z=T/math.sqrt(V); return z, 2*(1-norm.cdf(abs(z)))
rows=[]
for k in CODES:
    b=sum(p(r,k) for r in BASE); n1=sum(p(r,k) for r in E1); n2=sum(p(r,k) for r in E2); nn=sum(p(r,k) for r in NOWN); na=sum(p(r,k) for r in NOWA)
    pb=wilson(b,len(BASE)); pn=wilson(nn,len(NOWN))
    f=fisher_exact([[nn,len(NOWN)-nn],[b,len(BASE)-b]])[1]
    z,pt=cochran_armitage([E1,E2,NOWN],k)
    rows.append(dict(k=k,label=LABEL[k],e1=n1/len(E1),e2=n2/len(E2),base=pb[0],base_ci=(pb[1],pb[2]),now=pn[0],now_ci=(pn[1],pn[2]),nowall=na/len(NOWA),
                     delta=pn[0]-pb[0],p=f,trend_z=z,trend_p=pt))
rows.sort(key=lambda r:-r["delta"])
print(f"n: 2020-21={len(E1)} 2024-25={len(E2)} baseline={len(BASE)} 2026 NYC={len(NOWN)} 2026 all={len(NOWA)}")
print(f"{'code':6s} {'20-21':>6s} {'24-25':>6s} {'base':>6s} {'2026N':>6s} {'delta':>6s} {'fisher':>7s} {'trendz':>6s} {'trendp':>7s}")
for r in rows:
    print(f"{r['k']:6s} {r['e1']*100:6.0f} {r['e2']*100:6.0f} {r['base']*100:6.0f} {r['now']*100:6.0f} {r['delta']*100:+6.0f} {r['p']:7.3f} {r['trend_z']:6.2f} {r['trend_p']:7.3f}  {r['label']}")
# composite AI index: any of aip/aiu/aib/aig
def ai_any(r): return 1 if any(r["c"][k]>=1 for k in ("aip","aiu","aib","aig")) else 0
def ai_cand(r): return 1 if any(r["c"][k]>=1 for k in ("aiu","aib")) else 0
for nm,g in (("2020-21",E1),("2024-25",E2),("base",BASE),("2026 NYC",NOWN),("2026 all",NOWA)):
    print(f"AI any {nm}: {sum(ai_any(r) for r in g)}/{len(g)}  candidate-AI: {sum(ai_cand(r) for r in g)}/{len(g)}")
print("fisher AI-any base vs 2026NYC", fisher_exact([[sum(ai_any(r) for r in NOWN),len(NOWN)-sum(ai_any(r) for r in NOWN)],[sum(ai_any(r) for r in BASE),len(BASE)-sum(ai_any(r) for r in BASE)]])[1])
print("fisher cand-AI base vs 2026NYC", fisher_exact([[sum(ai_cand(r) for r in NOWN),len(NOWN)-sum(ai_cand(r) for r in NOWN)],[sum(ai_cand(r) for r in BASE),len(BASE)-sum(ai_cand(r) for r in BASE)]])[1])
# breadth: number of partner types per posting
TYPES=("hyp","gsi","isv","agy","resl","mkt")
def breadth(r): return sum(p(r,k) for k in TYPES)
def codes_n(r): return sum(p(r,k) for k in CODES)
for nm,g in (("2020-21",E1),("2024-25",E2),("base",BASE),("2026 NYC",NOWN)):
    print(f"{nm}: partner-type breadth mean {np.mean([breadth(r) for r in g]):.2f}  codes/posting mean {np.mean([codes_n(r) for r in g]):.1f}  median {np.median([codes_n(r) for r in g])}")
print("MWU breadth", mannwhitneyu([breadth(r) for r in NOWN],[breadth(r) for r in BASE]).pvalue, "MWU codes", mannwhitneyu([codes_n(r) for r in NOWN],[codes_n(r) for r in BASE]).pvalue)
# builder index
for nm,g in (("2020-21",E1),("2024-25",E2),("base",BASE),("2026 NYC",NOWN),("2026 all",NOWA)):
    vb=sum(r["vb"] for r in g); vm=sum(r["vm"] for r in g); print(f"builder {nm}: {vb}/{vb+vm} = {vb/(vb+vm):.2f}")
# years
for nm,g in (("base",BASE),("2026 NYC",NOWN)):
    y=[r["yrs"] for r in g if r["yrs"] and "unreliable" not in r.get("note","")]; print(f"years {nm}: n={len(y)} median {np.median(y)} mean {np.mean(y):.1f}")
# pay
def mids(g): return np.array([(r["bmin"]+r["bmax"])/2 for r in g if r.get("bmin") and r.get("bmax") and r.get("cur") in ("USD",None) and r["bmin"]!=r["bmax"] and "pay flagged" not in r.get("note","") and "looks low" not in r.get("note","")])
mb=mids(E2); mn=mids(NOWN)
print(f"pay 2024-25 n={len(mb)} median {np.median(mb):,.0f} IQR {np.percentile(mb,25):,.0f}-{np.percentile(mb,75):,.0f}")
print(f"pay 2026 NYC n={len(mn)} median {np.median(mn):,.0f} IQR {np.percentile(mn,25):,.0f}-{np.percentile(mn,75):,.0f}")
rng=np.random.default_rng(3); bs=[np.median(rng.choice(mn,len(mn)))-np.median(rng.choice(mb,len(mb))) for _ in range(5000)]
print("pay diff CI", np.percentile(bs,[2.5,50,97.5]))
# level mix
for nm,g in (("base",BASE),("2026 NYC",NOWN)):
    print(nm, collections.Counter(r["lvl"] for r in g))
# vocabulary: share of postings whose must-haves/phrases use term
TERMS={"AI":r"\bai\b|artificial intelligence|genai|llm|agent","partner-sourced":r"sourced|partner[- ]generated|partner[- ]led","pipeline":r"pipeline","co-sell":r"co[- ]sell","hyperscaler/cloud":r"aws|snowflake|azure|gcp|google cloud|hyperscaler|cloud",
       "build from zero":r"zero|from scratch|0 ?to ?1|founding|build","team":r"team|lead|manag","quota/revenue":r"quota|revenue|arr","executive":r"exec|c-level|c-suite|cxo"}
def txt(r): return " ".join(r["must"]+r["ph"]).lower()
for t,rx in TERMS.items():
    a=sum(1 for r in BASE if re.search(rx,txt(r))); b=sum(1 for r in NOWN if re.search(rx,txt(r)))
    print(f"term {t:18s} base {a}/{len(BASE)} ({a/len(BASE)*100:.0f}%)  2026NYC {b}/{len(NOWN)} ({b/len(NOWN)*100:.0f}%)  p={fisher_exact([[b,len(NOWN)-b],[a,len(BASE)-a]])[1]:.3f}")
json.dump(dict(rows=rows),open(__import__("os").path.join(__import__("os").path.dirname(__import__("os").path.abspath(__file__)),"then_now.json"),"w"),default=float,indent=0)
