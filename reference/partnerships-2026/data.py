# Coded 2026 niche postings. Codes: 2=required/core, 1=preferred/mentioned, absent=0.
# src = how the record was obtained: fetch (full page coded), manual (coded by analyst from indexed text), thin (page had little text)
CODES = ["src","infl","quota","arrn","fcst","hyp","gsi","isv","agy","resl","mkt","cos","res","oem","com","prog","deal",
         "aip","aiu","aib","aig","tech","mgr","pc","zero","csuite","jbp","tool","agyb","conb","hypb","stb","exec","intl","lang"]

def c(s):
    d = {k: 0 for k in CODES}
    for tok in s.split():
        k, v = tok[:-1], int(tok[-1])
        d[k] = v
    return d

R = []
def add(city, co, title, lvl, seg, bmin, bmax, cur, yrs, codes, must, ph, vb, vm, how="fetch", url="", note=""):
    R.append(dict(city=city, co=co, title=title, lvl=lvl, seg=seg, bmin=bmin, bmax=bmax, cur=cur, yrs=yrs,
                  c=c(codes), must=must, ph=ph, vb=vb, vm=vm, how=how, url=url, note=note))

# ---------------- NYC ----------------
add("NYC","GWI","VP Strategic Partnerships","VP","C",175000,200000,"USD",None,
    "src2 infl1 quota2 fcst2 isv2 cos2 com1 prog2 deal1 mgr2 csuite2 jbp1 tool1 exec1 intl2",
    ["Own partner-generated revenue and quota targets","Lead and develop the partner team","SaaS partnerships and ISV ecosystem leadership","Refine partner-driven sales processes across regions","Exceptional cross-cultural executive communication skills"],
    ["quota-carrying strategic role","Think big to make an impact"],4,5,url="https://job-boards.greenhouse.io/globalwebindex/jobs/8301393002")
add("NYC","Addepar","Head of Partner Solutions","Head","C",182000,285000,"USD",10,
    "src2 infl1 quota2 fcst2 gsi2 isv2 resl1 cos2 prog2 deal2 aip2 tech2 zero1 jbp2 stb1 exec1 intl2",
    ["Own partner-sourced revenue target with forecast accountability","Deep experience managing technical delivery partners","10+ years in partnerships or channel management","Executive influence and negotiation skills","Partner enablement and certification program design"],
    ["Partner Scorecard","total portfolio view"],6,1,url="https://job-boards.greenhouse.io/addepar1/jobs/8393340002")
add("NYC","Amperity","Head of Partnerships & Alliances","Head","B",178000,245000,"USD",5,
    "src2 infl2 fcst2 hyp2 gsi2 isv2 agy2 mkt2 cos2 com2 prog2 deal2 aip2 tech1 pc2 zero2 csuite2 jbp1 tool2 agyb1 hypb2",
    ["Own partner sourcing, structuring, and closing","Hands-on hyperscaler marketplace experience required","SI and agency partner relationship management","Salesforce pipeline and forecast management","Frequent travel and in-person fieldwork"],
    ["Return on cognition, not return on hype","hands-on, individual contributor role","AI-Curious Mindset"],7,3,url="https://jobs.madrona.com/companies/amperity/jobs/91216729-head-of-partnerships-alliances")
add("NYC","Hex","Head of Partnerships & Alliances","Head","A",None,None,None,None,
    "gsi2 agy2 aip2 mgr2",
    ["Define and drive key partnership strategies","Expand distribution through SI and agency ecosystems","Track record building successful partnerships","Developing high-performing teams","Outcomes-first approach to strategy and execution"],
    ["outcomes-first approach to strategy and execution"],1,0,how="thin",url="https://www.mediabistro.com/jobs/2959058842-head-of-partnerships-alliances")
add("NYC","Amplemarket","Head of Partnerships","Head","A",None,None,None,5,
    "src2 quota2 fcst2 isv1 resl1 prog2 deal1 aip2 tech1 mgr2 zero1 jbp2 exec2",
    ["Own partnerships channel end-to-end","5+ years partnerships or channel experience","Scaled disciplined partner program track record","Owned partner channel revenue number 2+ years","Fluent with sales leadership and AEs"],
    ["build a scalable and disciplined partner program","Manage channel conflict"],7,2,url="https://www.builtinnyc.com/job/head-partnerships/11249293")
add("NYC","Conveo","Head of Partnerships","Head","A",160000,260000,"USD",None,
    "src2 infl1 gsi2 isv2 agy2 resl2 cos2 res1 oem1 com1 prog2 deal2 aip2 tech1 mgr1 pc2 zero2 csuite1 agyb1 conb1 stb1 exec1",
    ["Build partnerships function from zero","Commercial and sales background to close deals","Deep research and insights landscape knowledge","Builder mentality over managing existing operations","Network to open doors and sell through partners"],
    ["build this function from zero","a build role with commercial teeth","a partner program that compounds"],4,0,url="https://www.builtinnyc.com/job/head-partnerships/9500849",note="yrs coded as 20 by extractor; treated as unreliable")
add("NYC","Botify","Head of Partnerships","Head","A",None,None,None,10,
    "src2 fcst2 hyp2 gsi2 agy2 prog2 deal2 aip2 aiu1 tech1 mgr1 pc2 zero2 agyb1 conb1 hypb2 intl2",
    ["Design partnership programs across agencies, consultancies, hyperscalers","Build partner organization from minimal footprint globally","Turn partnerships into measurable lead generation engine","Design commercial packaging and deal registration processes","Define partnership targets, forecasts, and metrics"],
    ["true lead gen engine","agency friendly program"],1,0,url="https://jobs.botify.com/jobs/177522-head-of-partnerships")
add("NYC","Decagon","Founding Head of Strategic Partnerships & Alliances","Head","A",None,None,None,7,
    "hyp2 isv1 deal2 aip2 pc1 zero2 stb2",
    ["7+ years in high-growth partnership roles","Excellent negotiation skills","Strong relationship management skills","Build relationships with major cloud providers","Lead negotiations with AI partners"],
    ["influencing product strategies"],1,0,how="thin",url="https://www.mediabistro.com/jobs/2364250214-founding-head-of-strategic-partnerships-alliances")
add("NYC","Insider One","Global Director, Data Cloud Alliances","Dir","B",None,None,None,10,
    "src2 infl1 quota1 fcst1 hyp1 isv2 cos2 com2 prog1 deal2 aip1 tech1 jbp2 intl2",
    ["10+ years partner sales and business development","Manage relationships with data platform providers","Drive partner-sourced pipeline and revenue growth","Solution selling with joint Insider-partner offerings","Negotiate annual business plans with partners"],
    ["Selection, Onboarding and Transacting with the Partners","go-to-market engine is primed and enabled"],2,3,url="https://www.builtinnyc.com/job/global-data-partnership-director/9068521")
add("NYC","Subtotal","Head of Partnerships","Head","B",140000,180000,"USD",4,
    "src2 infl1 gsi1 isv2 agy2 resl1 com2 cos1 prog2 deal1 tech1 pc1 zero2 csuite1 tool1 stb1",
    ["4+ years partnerships or channel experience","Track record scaling partner channel revenue","Balances program strategy with hands-on execution","Strong relationship-building with operators and founders","Cross-functional work with engineering and marketing"],
    ["a real revenue engine","the playbook is still being written"],2,0,url="https://www.ziprecruiter.com/c/Subtotal/Job/Head-of-Partnerships/-in-New-York,NY?jid=cf0970f56f8a32c0")
add("NYC","Profound","VP, Strategic Partnerships","VP","A",None,None,None,7,
    "src2 hyp2 gsi2 isv2 agy2 resl1 mkt2 cos2 com2 prog2 deal2 aip2 aiu2 tech1 mgr2 pc1 zero1 jbp2 agyb1 hypb2 stb2 exec2 intl2",
    ["Lead global partnership strategy with pipeline accountability","Deep experience running a GSI program","Agency ecosystem navigation and alliances","Hands-on hyperscaler co-sell and marketplace experience","Complex executive-level partnership deal negotiation"],
    ["architect and lead the global partnership strategy","definitive platform for AI search optimization"],6,1,url="https://www.tryprofound.com/careers/816c2ab6-7398-4cd8-b1b5-695d4673b476")
add("NYC","Yobi","Director, Sales & Partnerships","Dir","B",160000,200000,"USD",8,
    "src2 infl2 hyp1 isv2 agy2 cos2 com1 aip1 pc2 zero1 jbp2 agyb1 hypb1 stb2",
    ["8+ years enterprise AdTech or MarTech sales","Closing complex Fortune 500 advertiser deals","Proven partner-led and alliance co-selling success","Deep network across brands, agencies, platforms","Player-coach willing to prospect directly"],
    ["highly senior IC role","player-coach mentality","partner-led selling"],3,0,url="https://www.mediabistro.com/jobs/3539845292-director-sales-partnerships")
add("NYC","TripleLift","VP, Business Development","VP","B",250000,325000,"USD",8,
    "src1 quota1 fcst1 isv1 agy2 deal2 tech1 mgr2 csuite2 jbp1 exec1 intl2",
    ["Global business development strategy execution","Proven AdTech revenue growth and partnerships","Leading multi-region high-performing teams","Strong negotiation and deal-making skills","Deep DSP, SSP, CTV, clean room expertise"],
    ["Retail Media and Search Ads platforms"],2,3,url="https://www.mediabistro.com/jobs/3451483081-vp-business-development")
add("NYC","TripleLift","Platform Partnerships Director","Dir","B",140000,190000,"USD",5,
    "fcst1 isv2 cos1 com1 deal2 tech1 zero1 jbp1 tool1 exec1 intl1 conb1",
    ["5+ years programmatic advertising experience","Deep understanding of programmatic ecosystem","Extensive experience managing contract negotiations","Proven track record closing market-moving deals","Outstanding oral and written communication skills"],
    ["individual contributor, director-level role","closing market-moving deals"],4,5,url="https://jobs.edisonpartners.com/companies/triplelift/jobs/85615438-platform-partnerships-director")
add("NYC","Denodo","Strategic Alliances Manager/Director","Dir","C",None,None,"USD",5,
    "src2 infl2 quota1 fcst1 hyp2 isv2 cos2 com2 deal2 aip1 tech1 jbp2 tool1",
    ["Proven partnership track record driving joint GTM revenue","5+ years strategic alliances or partner management","Experience managing Tier 1 technology partners","Co-sell, co-build, co-market initiatives driving pipeline","Strong negotiation and cross-functional influence skills"],
    ["Sell Together - engaging referral and co-sell motions","better together joint value propositions"],3,3,url="https://denodo.com/kr/node/28415",note="single pay figure 180000 not a range; excluded from pay")
add("NYC","DataSnipper","Director of Partnerships","Dir","A",None,None,None,5,
    "src1 quota1 fcst1 isv2 com2 prog1 deal2 aip2 tech1 csuite2 jbp1 tool2 stb1 intl1",
    ["Lead partnership strategy and alliance growth","Strong negotiation and analytical skills required","Proven track record exceeding partnership targets","5+ years managing partnership programs","Oversee partner integrations and onboarding processes"],
    ["AI-powered audit ecosystem","Reporting directly to the CRO"],6,4,url="https://jobs.recruiter.com/jobs/12928518886-director-of-partnerships",note="pay figure unclear (possibly OTE); excluded")
add("NYC","Confidential (public cloud platform)","Head of AI Partnerships","Head","D",None,None,None,None,
    "src1 isv1 aip2 aiu1 tech1 exec2 stb1",
    ["Track record building strategic partnerships","Strong understanding of AI ecosystems and GPU infrastructure","Ability to handle technical and commercial conversations","Strong commercial mindset with revenue focus","Excellent leadership and communication skills"],
    ["measurable revenue impact","at the forefront of enterprise AI adoption"],2,1,url="https://talents.vaia.com/companies/confidential/new-york-city/head-of-ai-partnerships-108482741/")
add("NYC","Truthset","Director of Data Partnerships","Dir","C",160000,240000,"USD",None,
    "src1 fcst1 isv1 prog1 tech2 pc1 zero1 csuite1 jbp1 stb2 exec1",
    ["Lead Data Collective partner relationships and client service","Expand data strategy beyond consumer demographics","Deliver quarterly accuracy reports to data providers","Strong technical acumen for executive presentations","Thrive in fast-paced start-up environment"],
    ["figure-it-out attitude"],1,3,url="https://jobs.gusto.com/postings/truthset-inc-director-of-data-partnerships-1269becc-17e3-4521-9c98-fdb0d90a6737",note="posting date unverified")
add("NYC","Smartly","VP, Partner Development","VP","B",200000,265000,"USD",10,
    "src1 fcst1 isv2 cos2 prog1 deal2 aip2 tech2 mgr2 pc2 jbp1 exec2 intl1",
    ["Lead and mentor partner development team","Define partnership strategy for creative and measurement","Lead complex commercial and technical negotiations","Deep paid social and measurement ecosystem knowledge","Manage C-level relationships across major platforms"],
    ["Leads a small, high-performing team","Lead complex commercial negotiations"],3,0,url="https://job-boards.greenhouse.io/smartlyio/jobs/5751247004")
add("NYC","Confidential (AI / digital marketing)","Strategic Partnerships Director","Dir","A",230000,260000,"USD",10,
    "src1 isv2 resl1 prog1 deal2 aip1 aiu1 mgr1 zero1 csuite1 conb1 stb1 exec1",
    ["10+ years in partnerships or business development","Proven record closing complex enterprise platform partnerships","Strong executive presence and communication skills","Commercial judgment and deal structuring ability","Comfort in fast-paced, high-ownership environment"],
    ["originate, structure, and close complex partnerships","polished, strategic operator"],4,2,url="https://app.loxo.co/job/MTg5MDMtYXg0NzZ1aHZuM3lzbXFtMA==")
add("NYC","Braze","Senior Partner Account Director (Snowflake)","SrDir","B",187500,221250,"USD",8,
    "src2 infl2 isv2 cos1 prog1 aip1 tech2 zero1 exec2 jbp2 intl2",
    ["Deep Snowflake Data Cloud architecture knowledge","Global Braze-Snowflake partnership strategy ownership","C-suite executive alignment and governance design","Partner-sourced pipeline and revenue targets","Cross-functional influence without authority, matrixed organization"],
    ["strategic ambassador for the Braze-Snowflake partnership","first-in-kind capacity"],4,0,url="https://job-boards.greenhouse.io/Braze/jobs/7778126")
add("NYC","Braze","AVP, Partner Sales","VP","B",111000,166000,"USD",10,
    "src2 infl2 quota2 hyp1 gsi2 isv2 agy2 resl1 mkt1 com1 tech1 mgr2 zero2 csuite1 jbp2 agyb1 hypb2 stb1 exec2 intl2",
    ["Own global partner sales function strategy","Lead three regional Directors and their teams","Own global partner-influenced revenue targets","Carry VP and C-suite partner relationships","10+ years partner sales with Director-level management"],
    ["Leader of leaders","Comfortable with ambiguity and building structure"],8,4,url="https://jobera.com/job/braze-avp-partner-sales-a7fab87a/",note="aggregator pay range looks low; pay flagged")
add("NYC","Confidential (martech)","Head of Partnerships","Head","B",None,None,None,None,
    "src2 fcst2 isv2 agy2 cos2 prog1 pc2 zero2 agyb1 stb2",
    ["Proven partnership, BD, or sales revenue track record","Built programs or channels from scratch","Comfort in minimal-structure startup environments","Digital, performance, or adtech ecosystem experience","Strong commercial instincts and performance-driven mindset"],
    ["build-from-scratch environments","uncapped commission structure"],5,0,url="https://www.goodwinrecruiting.com/job/a0wr7000002fwenmaa-head-of-partnerships-adtech-new-york-new-york?amp=1")
add("NYC","Braze","Director, Strategic Technology Partnerships","Dir","B",95800,136900,"USD",None,
    "src2 infl2 quota1 fcst1 hyp2 isv2 cos2 com1 tech1 jbp1 exec1 intl2",
    ["Lead strategic AWS and Snowflake partner relationships","Shape global partner strategy with measurable goals","Drive joint product innovation and integrations","Deliver partner-sourced pipeline and revenue outcomes","Build senior relationships within partner organizations"],
    ["go-to partner in the technology ecosystem","co-selling initiatives"],5,1,url="https://www.sonara.ai/job-details/d751aae6-6f89-1d01-8f01-534736172f97",note="aggregator pay range looks low; pay flagged")
add("NYC","Braze","Director, Partner Sales","Dir","B",97000,145000,"USD",None,
    "src2 infl2 quota2 fcst2 hyp1 gsi2 isv2 agy2 resl1 mkt1 cos2 aip1 mgr2 pc2 jbp2 tool2 stb1 exec1 intl1",
    ["Lead regional partner sales team in B2B SaaS","Activate partner value within direct deal cycles","Work across SI and technology partners","Strong Salesforce proficiency for pipeline reporting","Influence sales org without formal authority"],
    ["player-coach role","Partner-influenced deals at Braze close"],5,3,url="https://www.themuse.com/jobs/braze/director-partner-sales",note="pay flagged")
add("NYC","Glean","Private Equity Partnerships Manager (Sr Mgr-Dir)","Mgr","A",250000,300000,"USD",5,
    "src2 infl1 quota2 fcst2 gsi1 isv1 cos1 prog1 deal2 aip2 aiu2 tech1 jbp2 tool1 conb1 exec2",
    ["Drive PE partnership strategy and deal management","Negotiate PE partnership agreements and preferred pricing","Primary contact for multiple PE sponsors","Own pipeline and revenue targets for sponsors","Fluency in PE economics and agentic AI"],
    ["lighthouse PortCo plays","Work AI platform"],2,6,url="https://www.marketingmonk.so/jobboard/jobs/private-equity-partnerships-manager-at-glean-8me9t1")
add("NYC","Persado","Director of Partnerships, Strategic Alliances","Dir","B",165000,185000,"USD",8,
    "src2 quota2 arrn2 fcst2 hyp1 isv2 cos2 deal1 aip2 pc2 zero2 csuite2 jbp2",
    ["Revenue-carrying owner of partner-sourced ARR","Scaled partnerships generating $3M-$5M+ ARR","Owned or influenced $2M+ partner-sourced ARR","Co-sell execution with ISV partners","Closing $500K+ ACV enterprise deals"],
    ["revenue-carrying Director, Strategic Alliances","prove the model before it scales"],4,0,how="manual",url="https://www.theladders.com/job/director-of-partnerships-strategic-alliances-persado-new-york-ny_86858599",note="page fetch failed; coded from indexed posting text")
add("NYC","OpenAI","Partner Director, Head of Technology Partnerships","Head","A",378000,420000,"USD",None,
    "fcst1 hyp1 isv2 cos1 prog1 deal1 aip2 aig1 tech1 mgr1 jbp2 exec2 intl1",
    ["Own and grow strategic ISV technology partnership portfolio","Define partnership strategy, priorities, and execution roadmap","Establish operating model with governance and cadence","Build joint go-to-market plans with Field and Marketing","Partner with Product and Engineering on integrations"],
    ["decision-ready memos, plans, and executive updates","Strong technical and product fluency"],3,0,url="https://jobs.khoslaventures.com/companies/openai/jobs/68478535-partner-director-head-of-technology-partnerships")
add("NYC","OpenAI","Partner Director, Global McKinsey Alliance","Dir","A",425000,425000,"USD",5,
    "src1 fcst1 gsi2 cos2 prog1 deal1 aip2 aiu1 tech1 mgr2 zero1 jbp2 conb2 exec2 intl2",
    ["Own global McKinsey relationship end-to-end","Lead co-selling of CxO-level AI opportunities","Define and run joint operating model","Executive engagement with CEOs, CIOs, Boards","Proven global multi-year partnership ownership"],
    ["single accountable executive owner of the McKinsey relationship","lighthouse account selection"],4,2,url="https://pitchmeai.com/jobs/openai/partner-director-global-mckinsey-alliance-lzlo7ydw13",note="single pay figure; excluded from range analysis")
add("NYC","OpenAI","Partner Director, Global Capgemini Alliance","Head","A",None,None,None,8,
    "src1 quota1 gsi2 cos2 prog2 deal1 aip2 aiu1 tech1 mgr2 zero1 jbp1 conb1 exec2 intl2",
    ["Own global Capgemini alliance P&L and growth","Global SI leadership and senior Capgemini relationships","Co-sell large complex enterprise AI transformations","Govern tiered benefits and delivery quality standards","8-12+ years partnerships or growth experience"],
    ["single accountable executive owner of the alliance","operating system for hundreds of joint clients"],4,0,url="https://aplyr.ai/jobs/469d3bd74878/partner-director-global-capgemini-alliance")
add("NYC","OpenAI","B2B Ecosystem Lead, Business Development","Mgr","A",None,None,None,8,
    "fcst1 isv2 cos2 prog1 deal2 aip2 aiu1 tech1 zero1 jbp1",
    ["8+ years in business development or partnerships","Take partnerships from pilot through sustained adoption","Negotiate product and commercial partnership agreements","Build business cases and partnership plans","Move projects forward without formal authority"],
    ["hands-on individual contributor role","small and fast-moving B2B partnerships team"],4,4,url="https://jobs.thrivecap.com/companies/openai/jobs/92728170-head-of-partnerships-digital-natives")
add("NYC","OpenAI","Partner Director, AWS Alliances","Dir","A",None,None,None,8,
    "src2 infl1 hyp2 mkt2 cos2 prog1 deal1 aip2 aiu1 tech2 zero1 jbp2 hypb2 stb1 exec2",
    ["8+ years partnerships or cloud alliances experience","Deep AWS field and co-sell motion experience","Proven partner-driven revenue track record","Complex enterprise deal support experience","Executive engagement with CIOs and CTOs"],
    ["field enablement, disciplined co-sell execution","ACE, Marketplace, opportunity tracking"],3,2,url="https://www.sonara.ai/job-details/partner-director-at-openai-5f932ac0-bddf-5fce-ccde-ac7ac5e82452")

# ---------------- PARIS ----------------
add("PAR","Partoo","Head of Partnerships","Head","B",90000,125000,"EUR",8,
    "src2 infl2 quota1 fcst2 gsi2 isv2 agy2 resl2 cos2 res2 com2 prog2 deal2 aip1 tech1 zero2 mgr1 pc2 csuite2 jbp2 exec1 intl2 lang2",
    ["Proven indirect ARR and pipeline generation through partners","5+ years B2B SaaS partnerships or channel sales","Negotiating VAR, referral, and tech integration contracts","Building reseller and partner ecosystem across EMEA","Hands-on ownership of partner operations and enablement"],
    ["Partnerships are a top strategic priority","Strategic and hands-on: you set the vision"],6,0,url="https://www.welcometothejungle.com/en/companies/partoo/jobs/head-of-partnerships-cdi-paris-m-f-d_paris_PARTO_59gJ0oM",note="range per WTTJ listing 90-125K")
add("PAR","Payflows","Head of Partnerships/Alliances","Head","A",None,None,None,5,
    "src2 infl1 fcst1 gsi2 isv2 resl1 cos2 com2 prog2 deal1 aip2 zero2 csuite1 jbp1 conb1 stb1 exec1 intl1",
    ["5+ years in partnerships or business development","Network across PE, ERP, or finance advisory in EMEA","Strong commercial instincts on partner and CFO buying","Track record of sourcing pipeline through partners","Excellent communication across CFOs, founders, and alliance leads"],
    ["founding role","build the function from zero","partnership-sourced revenue as a first-class number"],4,0,url="https://www.ziprecruiter.fr/jobs/546045747-head-of-partnerships-alliances-a-payflows")
add("PAR","ChapsVision","Head of Partner Ecosystem - Data & AI Solutions","Head","A",None,None,None,8,
    "src1 fcst2 gsi2 isv2 resl2 com1 prog2 deal2 aip2 tech1 jbp1 tool1 intl2 lang2",
    ["8+ years partnership definition and management experience","Strong European market and Data & AI knowledge","Excellent communication, negotiation, complex relationship management","Fluent English required","CRM and reporting tools mastery"],
    ["Structurer, developper et animer l'ecosysteme de partenaires","Anglais courant indispensable"],0,2,url="https://www.welcometothejungle.com/fr/companies/chapsvision/jobs/head-of-partner-ecosystem-data-ai-solutions_paris")
add("PAR","Mistral AI","Director of Systems Integrators","Dir","A",None,None,None,None,
    "src1 infl1 hyp1 gsi2 prog1 deal2 aip2 aiu1 tech1 mgr2 pc2 zero2 csuite1 jbp2 hypb1 stb2 exec2 intl2",
    ["Build and scale SI partnerships at top companies","Player-coach who closes high-stakes deals","Builder mentality for early-stage high-growth environments","Understanding of AI/ML deployment and cloud architectures","C-level executive presence and stakeholder alignment"],
    ["turning top GSIs into strategic growth engines","Player-coach","Builder mentality"],3,0,url="https://jobs.lever.co/mistral/59407c00-6d99-468d-bca6-5fd6b02bec7b")
add("PAR","Anthropic","Head of Southern Europe Partnerships","Head","A",160000,220000,"EUR",5,
    "src1 infl1 fcst2 gsi2 isv2 resl1 cos1 prog2 aip2 aiu2 tech1 pc2 zero2 jbp2 conb1 stb1 intl2 lang2",
    ["5+ years developing AI or enterprise service partners","Operational excellence managing multi-threaded partner programs independently","Managing partner ecosystem across multiple countries","Fluent French required; Spanish or Italian preferred","Hands-on 0-1 operator comfortable with high ambiguity"],
    ["voice of the partner","embedding partners into active sales cycles","first hire in region"],1,2,url="https://www.jobleads.com/fr/job/head-of-southern-europe-partnerships--paris--e3b2fe542690151966e8118b836967fec")
add("PAR","Mirakl","Director of Strategic Partnerships, Mirakl Ads","Dir","B",None,None,None,10,
    "src1 quota2 gsi1 isv1 agy2 cos2 oem1 com2 deal1 zero1 jbp1 exec1 intl2 lang1",
    ["10+ years in partnerships, BD, or sales","Proven record building high-impact strategic partnerships","Strong executive presence with senior stakeholders","Owns revenue targets and KPIs","Global partner ecosystem leadership with up to 25% travel"],
    ["Global Lead of Ads Partnerships"],5,1,url="https://www.talentis.global/?p=669177",note="posting date unverified")
add("PAR","Dataiku","EMEA Technology Alliances Manager","Mgr","A",None,None,None,5,
    "src2 infl1 quota1 hyp2 isv2 cos2 com1 prog2 deal2 aip2 tech1 jbp2 hypb2 stb1 exec2 intl2 lang2",
    ["Grow major cloud and ISV technology partnerships","Build trusted sales and executive relationships","Assist closing enterprise deals with partners","Own continental strategic partnership development","5-10+ years enterprise sales or partnerships"],
    ["Technology Alliances business in EMEA","navigating within complex ecosystems"],3,2,url="https://job-boards.greenhouse.io/dataiku/jobs/5195597004",note="Manager title, senior scope (reports to VP)")
add("PAR","Dataiku","Partner & Alliances Manager, Southern Europe","Mgr","A",None,None,None,None,
    "src1 infl2 quota2 hyp1 gsi2 isv2 prog1 aip2 jbp1 exec1 intl1",
    ["Drive partner account engagement and sales goals","Own partner-related quota and territory plan","Recruit and nurture partners across the region","Build trusted relationships across partner ecosystem","Enable partner field execution and skill development"],
    ["creating the conditions where our strategic partners can thrive"],6,1,url="https://theorg.com/org/dataiku/jobs/partner-gtm-lead-southern-34fa37d3",note="Manager title; quota-carrying")
add("PAR","Qevlar AI","Head of Partnerships","Head","A",None,None,None,5,
    "src2 infl2 fcst1 hyp2 hypb1 isv2 resl2 mkt2 cos2 com1 prog2 aip2 tech1 pc2 zero2 jbp1 stb2 exec1 intl2",
    ["5-10 years in cybersecurity partnerships or channels","Proven track record building scalable partner motions","Strong MSSP and SIEM/XDR ecosystem exposure","Strong SOC operations and security toolchain understanding","Ability to build partner programs from scratch"],
    ["Operates well in Series A-style environments","No playbooks needed"],8,3,url="https://qevlar-1721317262.teamtailor.com/jobs/6814695-head-of-partnerships")
add("PAR","Anthropic","AWS Partnerships Lead, Southern Europe","Mgr","A",None,None,None,7,
    "src1 hyp2 cos2 aip2 hypb2 zero2 stb2 intl2 lang1 exec1 pc2",
    ["Own AWS co-sell and GTM motion across Southern Europe","Direct experience partnering with or inside a hyperscaler","7+ years enterprise tech mixing SaaS sales and partnerships","Built cloud partnerships from zero to one","Startup experience scaling EMEA from a small base"],
    ["drive joint pipeline","zero to one"],3,0,how="manual",url="https://www.growthtalent.org/empregos/partnerships/anthropic/partnerships-lead-southern-europe-anthropic.md",note="page fetch failed; coded from indexed posting text")

# ---------------- second independent coding (binary) for reliability ----------------
SECOND = {
 "GWI": dict(sourced=1,influenced=1,quota=1,hyperscaler=0,si=0,isv=1,agency=0,marketplace=0,cosell=1,program=1,negotiation=0,ai_product=0,ai_skill=0,people_mgmt=1,hands_on=1,from_scratch=0,exec_rel=0,intl=1),
 "Addepar": dict(sourced=1,influenced=1,quota=1,hyperscaler=0,si=1,isv=1,agency=0,marketplace=0,cosell=1,program=1,negotiation=1,ai_product=1,ai_skill=0,people_mgmt=0,hands_on=0,from_scratch=0,exec_rel=1,intl=1),
 "Amperity": dict(sourced=1,influenced=1,quota=0,hyperscaler=1,si=1,isv=1,agency=1,marketplace=1,cosell=1,program=1,negotiation=1,ai_product=1,ai_skill=0,people_mgmt=0,hands_on=1,from_scratch=1,exec_rel=0,intl=0),
 "Profound": dict(sourced=1,influenced=1,quota=1,hyperscaler=1,si=1,isv=1,agency=1,marketplace=1,cosell=1,program=1,negotiation=1,ai_product=1,ai_skill=1,people_mgmt=1,hands_on=1,from_scratch=1,exec_rel=1,intl=1),
 "Smartly": dict(sourced=0,influenced=1,quota=0,hyperscaler=0,si=0,isv=1,agency=0,marketplace=0,cosell=1,program=1,negotiation=1,ai_product=1,ai_skill=0,people_mgmt=1,hands_on=1,from_scratch=0,exec_rel=1,intl=0),
 "Braze AVP": dict(sourced=1,influenced=1,quota=1,hyperscaler=1,si=1,isv=1,agency=1,marketplace=0,cosell=0,program=0,negotiation=0,ai_product=0,ai_skill=0,people_mgmt=1,hands_on=0,from_scratch=1,exec_rel=1,intl=1),
 "Partoo": dict(sourced=1,influenced=1,quota=1,hyperscaler=0,si=1,isv=1,agency=1,marketplace=0,cosell=1,program=1,negotiation=1,ai_product=0,ai_skill=0,people_mgmt=1,hands_on=1,from_scratch=1,exec_rel=1,intl=1),
 "Dataiku EMEA": dict(sourced=0,influenced=1,quota=1,hyperscaler=1,si=0,isv=1,agency=0,marketplace=0,cosell=1,program=1,negotiation=1,ai_product=1,ai_skill=0,people_mgmt=0,hands_on=1,from_scratch=0,exec_rel=1,intl=1),
}
SECOND_MAP = {"GWI":("GWI","VP Strategic Partnerships"),"Addepar":("Addepar",None),"Amperity":("Amperity",None),"Profound":("Profound",None),
              "Smartly":("Smartly",None),"Braze AVP":("Braze","AVP, Partner Sales"),"Partoo":("Partoo",None),"Dataiku EMEA":("Dataiku","EMEA Technology Alliances Manager")}
CODE_FOR = dict(sourced="src",influenced="infl",quota="quota",hyperscaler="hyp",si="gsi",isv="isv",agency="agy",marketplace="mkt",cosell="cos",
                program="prog",negotiation="deal",ai_product="aip",ai_skill="aiu",people_mgmt="mgr",hands_on="pc",from_scratch="zero",exec_rel="exec",intl="intl")
