# Historical baseline: closed niche postings, NYC or remote-US listed on Built In NYC / career.com.
# era: "2020-21" (pre-GenAI, Built In legacy URL scheme, dated by in-text anchors) or "2024-25" (dated by Built In removal stamp / datePosted)
from data import c, CODES
H = []
def addh(era, date, co, title, lvl, seg, bmin, bmax, yrs, codes, must, ph, vb, vm, url, note=""):
    H.append(dict(era=era, date=date, city="NYC", co=co, title=title, lvl=lvl, seg=seg, bmin=bmin, bmax=bmax, cur="USD" if bmin else None,
                  yrs=yrs, c=c(codes), must=must, ph=ph, vb=vb, vm=vm, how="fetch", url=url, note=note))

# ---------- 2020-21 (pre-GenAI) ----------
addh("2020-21","2020 (ID adjacent to Contentsquare 79013)","Simon Data","Head of Partnerships","Head","B",None,None,5,
 "src2 infl1 fcst1 gsi1 isv2 cos2 prog1 aip1 tech2 zero2",
 ["5-8 years across technology, solutioning, sales or strategy","2+ years in Marketing Technology","2+ years working with clients/prospects","Solid sales & presentation fundamentals","Technologically fluent with interfaces and integrations"],
 ["Own outreach, conversations, and outcomes with target partners","Technologically fluent; can quickly come to speed"],6,1,
 "https://www.builtinnyc.com/job/project/head-partnerships/77976")
addh("2020-21","2020 (cites May-2020 $190M Series D; post-COVID travel)","Contentsquare","Head of Technology Partnerships","Head","B",None,None,7,
 "src1 fcst1 isv2 cos1 prog2 deal1 tech1 pc1 jbp1 tool1 stb1 exec2 intl1",
 ["7+ years strategic/technology partnership experience","Lead and grow Technology Partner Program","Cultivate executive relationships with partners","Executive-level presentation creation and delivery","Travel to partner locations required"],
 ["first-of-their-kind partnership opportunities","roll up sleeves and dig deep to achieve goals"],7,1,
 "https://www.builtinnyc.com/job/project/head-technology-partnerships/79013")
addh("2020-21","2020-21 (legacy Built In ID 84125)","Movable Ink","Associate Director, Partner Sales","Mgr","B",None,None,3,
 "src2 infl2 quota2 gsi1 isv2 agy2 cos2 deal2 jbp1 agyb1",
 ["3+ years marketing technology SaaS sales","Partner-sourced opportunities against target prospect list","Closing large deals with partners","Co-sell with direct sales team","ESP, agency, or systems integrator partnership experience"],
 ["regionally aligned to support our direct sales team","Identify and sell in technical partner solutions"],5,2,
 "https://www.builtinnyc.com/job/sales/associate-director-partner-sales/84125")
addh("2020-21","2020-21 (legacy Built In ID 115608)","Movable Ink","Director, Commercial Partnerships","Dir","B",None,None,4,
 "src2 infl2 quota2 gsi1 isv2 agy2 cos2 prog1 deal2 mgr2 pc1 jbp2 intl1",
 ["4+ years marketing technology SaaS sales","revenue-driving ESP, agency, or SI partnerships","sourcing opportunities from partners against target lists","closing large partner deals to meet quotas","co-selling with direct sales teams"],
 ["Customers don't experience data, they experience content","activates any data into personalized content"],4,9,
 "https://www.builtinnyc.com/job/operations/director-commercial-partnerships/115608")
addh("2020-21","2021 (cites 2021 Gartner Magic Quadrant)","Dataiku","VP of Technology Alliances / Head of Technology Partnerships","VP","C",None,None,None,
 "src1 hyp2 gsi1 isv2 aip2 tech2 mgr2 stb1 exec1 intl2 hypb1",
 ["Expertise in modern AI/ML and cloud computing","Connections within Snowflake, AWS, Microsoft, Google, Tableau","Track record building partnerships with software and cloud companies","Experience leading a mature team with P&L responsibility","Hypergrowth software company experience ($50M to $500M)"],
 ["create joint offerings and integrations","Drive incremental recurring revenue"],4,1,
 "https://builtin.com/job/operations/head-technology-partnerships/256184", note="coded manually from fetched page text")

# ---------- 2024-25 ----------
addh("2024-25","removed 2025-06-25","Braze","Director, Strategic Technology Partnerships","Dir","B",95800,136900,None,
 "src1 infl2 fcst1 hyp2 isv2 cos2 com1 aip1 tech1 jbp2 exec1 intl2",
 ["Leads relationships with global technology partners like AWS and Snowflake","Shapes global partner strategy tied to shared business goals","Drives partner contributions to regional pipeline and revenue","Builds senior-level partner executive relationships","Runs joint go-to-market, co-selling, and campaign initiatives"],
 ["go-to partner in the technology ecosystem","Partner Account Managers (PAMs)"],7,1,
 "https://www.builtinnyc.com/job/director-strategic-technology-partnerships/6231125")
addh("2024-25","removed 2025-05-08","Magnite","Director, Strategic Partnerships","Dir","B",165000,185000,8,
 "src1 infl1 fcst2 isv2 com1 prog2 tech1 jbp1 tool2",
 ["8+ years AdTech commercial experience","Understanding of ad serving ecosystem","Experience with audience data vendors","Excellent written and verbal communication","Self-starter who initiates activity"],
 ["The capacity to act as a self-starter","Create a tactical executable strategy"],3,6,
 "https://www.builtinnyc.com/job/director-strategic-partnerships/4254679")
addh("2024-25","removed 2025-05-18","Attentive","Technology Partner Manager, ISV Partners","Mgr","B",120000,130000,5,
 "src2 infl1 isv2 cos2 com1 prog2 deal1 tech1 jbp1",
 ["5+ years partnership development experience","2+ years technology partnerships","Proven ISV partnership scaling and optimization","Track record of ISV-driven revenue growth","Marketing technology and industry trends knowledge"],
 ["champion for ISV partners within Attentive","Act Like an Owner"],9,2,
 "https://www.builtinnyc.com/job/technology-partner-manager-isv-partners/4426181", note="remote US, NYC-HQ employer")
addh("2024-25","removed 2025-07-18","Writer","Director, Product Partnerships","Dir","A",None,None,8,
 "src1 hyp1 isv2 mkt1 cos1 oem1 com2 deal2 aip2 aib1 tech2 pc2 zero2 jbp1 tool1 stb1",
 ["8+ years in product, data, or strategic partnerships","Owns partnerships end-to-end","Manages integrations with product and engineering","Familiarity with data licensing models","Confident negotiator with strong communication"],
 ["Thrives in a fast-paced, ambiguous environment","scrappiness is a superpower"],8,6,
 "https://www.builtinnyc.com/job/director-product-partnerships/6270102", note="remote US with NYC office")
addh("2024-25","removed 2025-05-08","Dataminr","Director, Platform Partnerships","Dir","A",144000,200000,8,
 "src2 infl1 quota1 fcst1 isv1 prog1 deal2 aip2 zero1 tool1 stb2 exec2 intl2",
 ["8+ years SaaS or high-growth data company experience","Continuous pipeline development, top to bottom of funnel","Metrics-driven GTM execution track record","Influence across C-level executives and team members","Bachelor's degree or equivalent work experience"],
 ["drive revenue growth across our AI ecosystem","build something from concept to execution"],7,3,
 "https://www.builtinnyc.com/job/director-platform-partnerships/4061892")
addh("2024-25","removed 2025-09-24 (posted 2025-09-20)","LiveRamp","Senior Director, AI Partnerships","Dir","C",250000,309000,5,
 "src1 fcst2 isv1 prog1 aip1 tech1 mgr2 pc2 zero1 stb1 intl1",
 ["5+ years in a management role","Strong network across AI businesses and startups","AdTech background a big plus","Track and forecast pipeline opportunities","Independent, self-sufficient, minimal management needed"],
 ["must have AI Ecosystem for our customers","Independent and self-sufficient"],3,1,
 "https://www.builtinnyc.com/job/senior-director-publisher-development/6789154")
addh("2024-25","removed 2025-03-06","Rokt (mParticle)","Director of Channel Partnerships, Solution Partners","Dir","B",170000,200000,5,
 "src2 infl2 quota1 gsi2 isv1 agy2 cos1 com1 prog2 deal1 aip2 tech1 pc2 jbp2 agyb1 conb1 stb2",
 ["5+ years channel or direct sales experience","Consultancy, SI, and digital agency landscape knowledge","Strong MarTech ecosystem familiarity","Hybrid NYC role, 4 days/week in-office","Willing to travel up to 25%"],
 ["source and influence new revenue","joint GTM plans and mutual commitments"],8,4,
 "https://builtin.com/job/director-channel-partnerships-solution-partners/3945787")
addh("2024-25","removed 2025-08-04","Yext","Director, Reseller (Agency Partnerships)","Dir","B",106650,207500,5,
 "src2 quota1 fcst2 isv1 agy2 resl2 res2 prog1 deal2 aip1 pc2 jbp1 tool2 agyb2 exec1",
 ["5+ years partner/reseller or agency sales","Proven record closing strategic partnerships and exceeding quota","Deep advertising agency ecosystem understanding","Familiarity with Salesforce and partner CRM","BA/BS degree or equivalent experience"],
 ["advertising agency ecosystem","Partner & Strategic Partner Division"],4,2,
 "https://www.builtinnyc.com/job/director-reseller-agency-partnerships/6445220")
addh("2024-25","removed 2025-05-30 (posted 2025-05-06)","LiveRamp","Client Partner, Technology Partnerships","Mgr","C",154500,181500,5,
 "quota2 isv1 deal2 tech1",
 ["5+ years quota-carrying sales/BD experience","Adtech, Martech, or SaaS sales background","Platform and data partnerships experience","Strategic consultative selling","Comfort with technical sales process"],
 ["Deliver against a revenue growth target","remarkably strategic, driven, and entrepreneurial"],2,0,
 "https://www.builtinnyc.com/job/client-partner/4541615")
addh("2024-25","removed 2025-07-23 (posted 2025-07-01)","Hightouch","Technology Partner Sales","Mgr","C",115000,220000,None,
 "src2 infl1 quota1 hyp1 isv2 cos1 com2 prog1 tech1 jbp1 exec1",
 ["Previous success with outbound sales","Previous success working with technology partners","Understanding of composable CDP space","Hunger for high volume activity","Ability to create creative campaigns"],
 ["Hunger for high volume activity","first principles thinking mindset"],5,0,
 "https://www.builtinnyc.com/job/technology-partnerships-sales/3698508", note="remote US")
addh("2024-25","removed 2025-05-15 (posted 2025-05-08)","Luminate","VP, Partnerships","VP","C",200000,250000,7,
 "src1 fcst1 isv1 deal2 tech1 mgr2 jbp1 tool2",
 ["7+ years in music/entertainment business development or partnerships","Deep music and VOD industry contacts","Track record of data partnerships with major players","Negotiation and stakeholder consensus-building skills","Experience leading small teams"],
 ["most essential, objective, and trustworthy data","Represent the company at industry events, conferences"],5,3,
 "https://www.builtinnyc.com/job/luminate-vp-partnerships/4434557")
addh("2024-25","posted 2025-04-24, closed 2025-05-24","Treasure Data","Director of Partnerships","Dir","B",200000,215000,7,
 "src2 infl1 quota1 fcst1 gsi2 isv2 agy1 com1 prog1 deal2 aip1 tech1 jbp2 conb2 exec2 intl1 lang2",
 ["7 years partnership management or sales leadership with Global SIs","Fluent in French","Bachelor's degree in business, marketing, or related field","Deep technology consulting industry understanding","Strong negotiation and contract management skills"],
 ["Must be fluent in French to effectively communicate","Previous experience working with Global System Integrators"],4,4,
 "https://career.com/job/treasure-data/director-of-partnerships/j202502250947487370381")
