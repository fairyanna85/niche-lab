import re, sys, math
sys.path.insert(0,'.')
from data import R
from scipy.stats import fisher_exact
# 2020 partnership job titles from the Cloud Software Association Slack job archive (posts dated Jan-Nov 2020), partnership roles only
T2020 = ["Director of Business Development, Strategic Alliances","Strategic Partners Account Manager","Senior Manager, Strategy Operations (Strategic Partnerships)",
"Partner Account Manager (Strategic Partnerships)","Channel Manager","Partner Manager","Strategic Partner Associate","Junior Channel Partner Manager",
"Junior Ecosystem Manager","Senior Ecosystem Manager","Director of Partner Managers","Partner Manager","Strategic Business Development Manager",
"Partner Manager, ISV partners","Channel Marketing Manager","Partnership & Integration Manager","Director of Partnerships","Manager, Technology Partnerships",
"Senior Partner Manager","Channel/Alliances Manager, North America","VP, Partnerships","VP of Partner Channels","Partner Account Manager",
"Senior Manager, Strategic Alliances","Partner Manager","Senior Manager, Global Channel Programs","Head of Strategic Partnerships","Cloud Partner Manager",
"Channel Partnerships Manager","Strategic Partner Manager","Head of Partnerships","Senior Manager, App Store","Partner Program Manager","Head of Partnerships",
"Alliance Lead (enterprise alliances)","Director of Channel","Microsoft Alliance Manager","Sage Alliance Manager","Partner Development Manager",
"Head of Partnerships","Partner Manager","Director of Strategic Partnerships & Channel"]
T2026 = [r["title"] for r in R]
feats = {
 "Alliance(s)": r"allian", "Channel": r"channel", "Ecosystem": r"ecosystem", "AI in title": r"\bai\b",
 "Named partner in title (AWS, Snowflake, McKinsey, Capgemini, Microsoft, Sage...)": r"aws|snowflake|mckinsey|capgemini|microsoft|sage|google|databricks",
 "Senior title (Head, Director, VP, SVP)": r"\bhead\b|director|\bvp\b|svp|avp|founding",
 "Manager-level title": r"manager", "Junior / associate": r"junior|associate",
 "'Strategic' in title": r"strategic", "Systems integrators / GSI in title": r"integrator|\bsi\b|gsi",
}
def wilson(k,n,z=1.96):
    p=k/n; den=1+z*z/n; c=(p+z*z/(2*n))/den; h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den; return p,max(0,c-h),min(1,c+h)
print(f"n2020={len(T2020)} n2026={len(T2026)}")
for name, pat in feats.items():
    a=sum(bool(re.search(pat,t.lower())) for t in T2020); b=sum(bool(re.search(pat,t.lower())) for t in T2026)
    p=fisher_exact([[a,len(T2020)-a],[b,len(T2026)-b]])[1]
    pa=wilson(a,len(T2020)); pb=wilson(b,len(T2026))
    print(f"{name:75s} 2020 {a:2d} ({pa[0]*100:4.0f}%)  2026 {b:2d} ({pb[0]*100:4.0f}%)  diff {100*(pb[0]-pa[0]):+5.0f}pt  Fisher p={p:.3f}")
