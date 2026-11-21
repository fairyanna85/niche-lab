import os, sys, json, re, math, random, itertools, collections
import numpy as np
sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
from data import R, CODES, SECOND, SECOND_MAP, CODE_FOR
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import pdist, squareform

LABEL = dict(src="Owns partner-sourced pipeline/revenue", infl="Partner-influenced revenue", quota="Carries a quota / revenue number",
 arrn="States a numeric ARR threshold", fcst="Forecasting / attribution / CRM reporting", hyp="Hyperscalers (AWS/GCP/Azure)",
 gsi="GSIs / SIs / consultancies", isv="ISV / technology / integration partners", agy="Agencies", resl="Resellers / VARs / channel",
 mkt="Cloud marketplaces", cos="Co-sell", res="Resale", oem="OEM / embedded", com="Co-marketing / partner funds",
 prog="Partner program design (tiers, incentives, enablement)", deal="Structures / negotiates complex deals", aip="Employer sells AI",
 aiu="Candidate must use / be fluent in AI", aib="Candidate builds AI agents / automation", aig="AI governance", tech="Technical depth (APIs, data stack)",
 mgr="Manages people", pc="Player-coach / hands-on IC", zero="Build from zero / founding role", csuite="Reports to C-level",
 jbp="Joint business plans / QBRs / account mapping", tool="Named tools (Salesforce, PRM, Crossbeam)", agyb="Agency background valued",
 conb="Consulting background valued", hypb="Hyperscaler experience required", stb="Startup / high-growth experience", exec="C-level relationships",
 intl="International / multi-region scope", lang="Languages required")

def wilson(k, n, z=1.96):
    if n == 0: return (0, 0, 0)
    p = k / n; den = 1 + z*z/n
    centre = (p + z*z/(2*n)) / den
    half = z*math.sqrt(p*(1-p)/n + z*z/(4*n*n)) / den
    return p, max(0, centre-half), min(1, centre+half)

def present(r, k): return 1 if r["c"][k] >= 1 else 0
def required(r, k): return 1 if r["c"][k] == 2 else 0

out = {}
groups = {"ALL": R, "NYC": [r for r in R if r["city"]=="NYC"], "PAR": [r for r in R if r["city"]=="PAR"],
          "SENIOR": [r for r in R if r["lvl"] in ("Head","VP","SVP")], "DIRMGR": [r for r in R if r["lvl"] in ("Mgr","Dir","SrDir")],
          "SEG_A": [r for r in R if r["seg"]=="A"], "SEG_BC": [r for r in R if r["seg"] in ("B","C")]}
out["n"] = {g: len(v) for g, v in groups.items()}

prev = {}
for k in CODES:
    row = {}
    for g, rs in groups.items():
        n = len(rs); kp = sum(present(r,k) for r in rs); kr = sum(required(r,k) for r in rs)
        p, lo, hi = wilson(kp, n)
        row[g] = dict(k=kp, n=n, p=round(p,3), lo=round(lo,3), hi=round(hi,3), req=kr)
    prev[k] = row
out["prev"] = prev

# ranking overall
rank = sorted(CODES, key=lambda k: -prev[k]["ALL"]["p"])
print("n:", out["n"])
print("\nPREVALENCE (present >=1), ALL / NYC / PAR / Senior(Head+VP) / Dir-Mgr / SegA / SegBC")
for k in rank:
    a = prev[k]
    print(f"{k:6s} {a['ALL']['k']:2d}/{a['ALL']['n']} {a['ALL']['p']*100:5.1f}% [{a['ALL']['lo']*100:4.0f}-{a['ALL']['hi']*100:3.0f}] req={a['ALL']['req']:2d} | NYC {a['NYC']['p']*100:4.0f} PAR {a['PAR']['p']*100:4.0f} | SEN {a['SENIOR']['p']*100:4.0f} DIR {a['DIRMGR']['p']*100:4.0f} | A {a['SEG_A']['p']*100:4.0f} BC {a['SEG_BC']['p']*100:4.0f}  {LABEL[k]}")

# seniority and segment gaps with Fisher exact
from scipy.stats import fisher_exact, mannwhitneyu
print("\nSENIORITY GAP (Head/VP vs Dir/Mgr) and SEGMENT GAP (A vs B/C), Fisher exact p")
gaps = []
for k in CODES:
    s = groups["SENIOR"]; d = groups["DIRMGR"]
    a1 = sum(present(r,k) for r in s); a2 = len(s)-a1; b1 = sum(present(r,k) for r in d); b2 = len(d)-b1
    p1 = fisher_exact([[a1,a2],[b1,b2]])[1]
    A = groups["SEG_A"]; B = groups["SEG_BC"]
    c1 = sum(present(r,k) for r in A); c2 = len(A)-c1; d1 = sum(present(r,k) for r in B); d2 = len(B)-d1
    p2 = fisher_exact([[c1,c2],[d1,d2]])[1]
    gaps.append((k, a1/len(s)-b1/len(d), p1, c1/len(A)-d1/len(B), p2))
for k, g1, p1, g2, p2 in sorted(gaps, key=lambda x: x[2]):
    if p1 < 0.25 or p2 < 0.25:
        print(f"{k:6s} senior-dir {g1*100:+5.0f}pt p={p1:.3f} | A-BC {g2*100:+5.0f}pt p={p2:.3f}  {LABEL[k]}")
out["gaps"] = gaps

# co-occurrence lift among codes present in >=25% of postings
X = np.array([[present(r,k) for k in CODES] for r in R])
freq = X.mean(0)
idx = [i for i,k in enumerate(CODES) if freq[i] >= 0.25]
pairs = []
for i, j in itertools.combinations(idx, 2):
    both = (X[:,i] & X[:,j]).mean()
    if both == 0: continue
    lift = both / (freq[i]*freq[j])
    n11 = int((X[:,i] & X[:,j]).sum()); n10 = int((X[:,i] & (1-X[:,j])).sum()); n01 = int(((1-X[:,i]) & X[:,j]).sum()); n00 = len(R)-n11-n10-n01
    p = fisher_exact([[n11,n10],[n01,n00]], alternative="greater")[1]
    pairs.append((CODES[i], CODES[j], round(lift,2), n11, round(p,3)))
pairs.sort(key=lambda x: (x[4], -x[2]))
print("\nTOP CO-OCCURRING PAIRS (lift, joint count, one-sided Fisher p)")
for p in pairs[:15]: print(p)
out["pairs"] = pairs[:25]

# clustering postings on binary codes (Jaccard, average linkage)
D = pdist(X, metric="jaccard")
Z = linkage(D, method="average")
for kc in (3, 4):
    lab = fcluster(Z, kc, criterion="maxclust")
    print(f"\nCLUSTERS k={kc}")
    for cl in sorted(set(lab)):
        mem = [R[i] for i in range(len(R)) if lab[i]==cl]
        Xm = X[lab==cl]; m = Xm.mean(0)
        dist = [(CODES[i], round(m[i]-freq[i],2), round(m[i],2)) for i in range(len(CODES))]
        top = sorted(dist, key=lambda x: -x[1])[:7]
        print(f" cluster {cl} n={len(mem)}: ", ", ".join(f"{r['co']}|{r['lvl']}" for r in mem))
        print("   over-indexed:", top)
lab4 = fcluster(Z, 4, criterion="maxclust"); lab3 = fcluster(Z, 3, criterion="maxclust")
out["clusters3"] = [(R[i]["co"], R[i]["title"], int(lab3[i])) for i in range(len(R))]

# outliers: mean Jaccard distance to others
S = squareform(D); md = S.mean(1)
print("\nOUTLIERS (highest mean Jaccard distance)")
for i in np.argsort(-md)[:6]: print(R[i]["co"], "|", R[i]["title"], round(md[i],3), R[i]["how"])

# pay (NYC USD ranges, exclude flagged)
pay = [r for r in R if r["city"]=="NYC" and r["bmin"] and r["bmax"] and r["bmin"]!=r["bmax"] and "pay flagged" not in r["note"] and "looks low" not in r["note"]]
mids = np.array([(r["bmin"]+r["bmax"])/2 for r in pay])
print(f"\nPAY NYC n={len(pay)} median midpoint {np.median(mids):,.0f}  IQR {np.percentile(mids,25):,.0f}-{np.percentile(mids,75):,.0f}")
for r in sorted(pay, key=lambda r: -(r['bmin']+r['bmax'])): print(f"  {r['co']:38s} {r['lvl']:5s} {r['bmin']:>7,}-{r['bmax']:>7,}")
rng = np.random.default_rng(7)
paygap = []
for k in CODES:
    w = np.array([present(r,k) for r in pay]).astype(bool)
    if w.sum() < 3 or (~w).sum() < 3: continue
    diff = np.median(mids[w]) - np.median(mids[~w])
    boots = []
    for _ in range(4000):
        a = rng.choice(mids[w], w.sum()); b = rng.choice(mids[~w], (~w).sum())
        boots.append(np.median(a)-np.median(b))
    lo, hi = np.percentile(boots, [2.5, 97.5])
    paygap.append((k, int(w.sum()), round(diff), round(lo), round(hi)))
paygap.sort(key=lambda x: -x[2])
print("PAY GAP by code (median midpoint with - without, bootstrap 95% CI)")
for p in paygap: print(" ", p, LABEL[p[0]])
out["pay"] = dict(n=len(pay), median=float(np.median(mids)), q1=float(np.percentile(mids,25)), q3=float(np.percentile(mids,75)), gaps=paygap)
paris_pay = [(r["co"], r["bmin"], r["bmax"]) for r in R if r["city"]=="PAR" and r["bmin"]]
print("PARIS PAY", paris_pay)

# years required
yrs = [r["yrs"] for r in R if r["yrs"] and "unreliable" not in r["note"]]
print(f"\nYEARS REQUIRED n={len(yrs)} median {np.median(yrs)} range {min(yrs)}-{max(yrs)}  dist {collections.Counter(yrs)}")
for g in ("SENIOR","DIRMGR"):
    y = [r["yrs"] for r in groups[g] if r["yrs"]]
    print(f"  {g}: median {np.median(y)} n={len(y)}")
out["yrs"] = dict(n=len(yrs), median=float(np.median(yrs)), counts=dict(collections.Counter(yrs)))

# verb register: builder index
for g in ("ALL","SENIOR","DIRMGR","NYC","PAR","SEG_A","SEG_BC"):
    vb = sum(r["vb"] for r in groups[g]); vm = sum(r["vm"] for r in groups[g])
    print(f"BUILDER INDEX {g}: build-verbs {vb} / manage-verbs {vm}  share build {vb/(vb+vm):.2f}")

# linguistic: tokens in requirement phrases
STOP = set("a an and the of in to for with or on at by as from into across over without within is are be your you our we their its it this that while not just than more most".split())
def toks(s):
    s = s.lower().replace("-", " ").replace("/", " ")
    return [w for w in re.findall(r"[a-z\$\+0-9]+", s) if w not in STOP and len(w) > 1]
def bigrams(t): return [" ".join(t[i:i+2]) for i in range(len(t)-1)]
docs = {i: toks(" ".join(r["must"]+r["ph"])) for i, r in enumerate(R)}
docfreq = collections.Counter()
for t in docs.values(): docfreq.update(set(t))
print("\nTOP TERMS by document frequency (share of postings using the word in their top requirements/phrases)")
print([(w, c) for w, c in docfreq.most_common(40)])
bdf = collections.Counter()
for t in docs.values(): bdf.update(set(bigrams(t)))
print("TOP BIGRAMS", [(w,c) for w,c in bdf.most_common(25)])

def logodds(ga, gb, prior_scale=1.0):
    ca = collections.Counter(); cb = collections.Counter(); call = collections.Counter()
    for i in ga: ca.update(docs[i])
    for i in gb: cb.update(docs[i])
    for t in docs.values(): call.update(t)
    a0 = sum(call.values()) * prior_scale
    na, nb = sum(ca.values()), sum(cb.values())
    res = []
    for w in call:
        aw = call[w]*prior_scale
        ya, yb = ca[w], cb[w]
        d = math.log((ya+aw)/(na+a0-ya-aw)) - math.log((yb+aw)/(nb+a0-yb-aw))
        var = 1/(ya+aw) + 1/(yb+aw)
        res.append((w, round(d/math.sqrt(var),2), ya, yb))
    res.sort(key=lambda x: -x[1])
    return res
sen = [i for i,r in enumerate(R) if r["lvl"] in ("Head","VP","SVP")]; dm = [i for i,r in enumerate(R) if r["lvl"] in ("Mgr","Dir","SrDir")]
lo = logodds(sen, dm)
print("\nKEYNESS Head/VP vs Dir/Mgr (z, count senior, count dir):", lo[:12], "\n  ...Dir/Mgr side:", lo[-12:])
segA = [i for i,r in enumerate(R) if r["seg"]=="A"]; segBC = [i for i,r in enumerate(R) if r["seg"] in ("B","C")]
lo2 = logodds(segA, segBC)
print("KEYNESS AI-native vs martech/data:", lo2[:12], "\n  ...B/C side:", lo2[-12:])
nyc = [i for i,r in enumerate(R) if r["city"]=="NYC"]; par = [i for i,r in enumerate(R) if r["city"]=="PAR"]
lo3 = logodds(par, nyc)
print("KEYNESS Paris vs NYC:", lo3[:12])

# reliability (Cohen's kappa) on double-coded subset
from sklearn.metrics import cohen_kappa_score
first, second = [], []
perc = {}
for key, sec in SECOND.items():
    co, title = SECOND_MAP[key]
    rec = [r for r in R if r["co"]==co and (title is None or r["title"]==title)][0]
    for kk, v in sec.items():
        code = CODE_FOR[kk]
        f = present(rec, code)
        first.append(f); second.append(v)
        perc.setdefault(code, []).append((f, v))
kap = cohen_kappa_score(first, second)
agree = np.mean(np.array(first)==np.array(second))
print(f"\nRELIABILITY pooled over {len(SECOND)} postings x 18 codes: agreement {agree:.2f}, Cohen kappa {kap:.2f}")
percode = {}
for code, pairs_ in perc.items():
    a = [p[0] for p in pairs_]; b = [p[1] for p in pairs_]
    ag = np.mean(np.array(a)==np.array(b))
    k = cohen_kappa_score(a, b) if len(set(a))>1 or len(set(b))>1 else float('nan')
    percode[code] = (round(ag,2), None if math.isnan(k) else round(k,2))
print("per code (agreement, kappa):", percode)
out["kappa"] = dict(pooled=float(kap), agree=float(agree), percode=percode)

json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"results.json"),"w"), indent=1, default=str)
