---
name: run
description: Career niche research from a resume and a LinkedIn profile. Asks once for both, then researches live job postings, finds and ranks 3–10 job-market niches for any profession, writes one tailored resume per niche, rewrites the LinkedIn profile, and fills an interactive HTML career report. Use when someone wants their resume analyzed against the market, wants to know which roles to target, or asks to run niche-lab.
---

# niche-lab: run

You are running a labor-market study for ONE person. Work in any profession: nothing here assumes a job family.

## Step 0: preflight (silent)

Run `python3 <skill>/scripts/preflight.py --json` (`<skill>` = the folder holding this file). It reports: web search, page fetch, package install, PDF reader, Chrome, subagents. Then:
- Install missing Python packages with `pip install -r <skill>/requirements.txt` (add `--break-system-packages` if pip asks).
- **No web search or no page fetch:** stop. Tell the person plainly that niche-lab needs web access to research postings and cannot run here. Do not run on the example corpus instead.
- **No subagents:** run the second coder and reviewers inline; gates then report reviews as "not independent".
- **No Chrome:** resumes are delivered as DOCX and Markdown; the PDF and ATS check are marked "not run".

## Step 1: the only question

Ask exactly one question, once, in the person's language:

> Please send your resume (PDF, Word or text) and your LinkedIn profile. For LinkedIn, the PDF export works best: on your profile, click **More → Save to PDF**. Pasting the profile text also works. A profile link alone usually cannot be read.

Then never ask anything else. If only a LinkedIn URL arrives, try one page fetch; if it fails, continue resume-only and say so in one line. Missing facts become `[placeholders]` and lines in the report's Confirm list.

## Step 2: tell them what happens

One short message: what you will deliver (one resume per niche, a LinkedIn rewrite, an interactive report), roughly how long a quick run takes, and that progress appears as a task list. Default depth is **quick** (3 niches, ~20 postings each). Use **full** (up to 10 niches, 30+ postings each) only if the person asks for depth.

## Step 3: run the phases

Create `runs/<slug>/` with `run_config.json` (`{"skill_version":"2.1.0","fictional":false,"relaxed":false,"depth":"quick","data_window":"…","language":"<detected>"}`). Keep a task list with one item per phase. Each phase file gives inputs, steps, rubric, output and the gate that must pass before moving on.

| Phase | File | Output |
|---|---|---|
| 0 Ingest | `phases/00-ingest.md` | resume.txt, parse_report.json, ledger.json |
| 1 Dissect | `phases/01-dissect.md` | profile.json, evidence.json |
| 2 Niches | `phases/02-niches.md` | niches.json |
| 2b Codebook | `phases/02b-induce-codebook.md` | codebooks/induced-<family>.yml for any family without a module |
| 3 Demand | `phases/03-demand.md` | postings/, niches/<id>/analysis.json |
| 4 Supply | `phases/04-supply.md` | peers.jsonl and peers.json per niche: people now in the jobs, from public announcements, team pages and speaker bios (≥ 8, else hidden) |
| 5 Prognosis | `phases/05-prognosis.md` | change block (or hidden); assemble adds the pooled trend, title shift and contrasts |
| 6 Rank | `phases/06-rank.md` | fit, qualification, ranking, fit_per_posting, fix_ladder |
| 7 Target | `phases/07-target.md` | access, employers, narrative niche blocks, golden formulas, the 12-week plan |
| 8 Rewrite | `phases/08-rewrite.md` | resumes.json |
| 8b LinkedIn | `phases/08b-linkedin.md` | linkedin.json |
| 9 Gates | `phases/09-gates.md` | gates.json, baseline.json, reviews/, the blind old-vs-new panel |
| 10 Assemble | `phases/10-assemble.md` | journey text and three findings in narrative.json; results.json, out/report.html, out/resume-*.{docx,pdf,md} |

## Step 4: deliver

Send, in this order: the report (publish as an artifact if an artifact tool exists, otherwise send the HTML file), one resume per niche (DOCX, plus PDF when Chrome exists), and `linkedin.md`. Then three lines: the niches to run now, the first fix, the number of items to confirm. Do not recap the steps.

Deliverables, by name: **one resume per niche**, a **LinkedIn rewrite**, and the interactive **report** (the career copilot).

## Hard rules

- **One question only.** Never ask the person anything after step 1.
- **Traceability.** Every resume and LinkedIn number, title, employer and date appears in a ledger line. `gates.py` enforces it.
- **One fact base.** All versions share the ledger; dates and titles never differ.
- **Grades.** Every inferred field is `stated`, `inferred2`, `inferred1` or `absent`.
- **Raw text first.** Store every posting's full text before coding it.
- **Sample-size honesty.** Tests at n ≥ 30 per group; below that, counts only and "low confidence".
- **Hide, don't pad.** Empty chapters are null with a reason.
- **Advice everywhere.** Every section has a non-empty `do_this`; every action has impact, effort and a source section.
- **Privacy.** No private individual's name in the report; peers stored as hashes.
- **Sources.** Every external figure cites a URL from `rulebook/sources.md` or one fetched in this run.

## Subagents

In the plugin, use the agents `niche-lab:second-coder`, `niche-lab:advocate`, `niche-lab:reviewer-recruiter`, `niche-lab:reviewer-hiring-manager`, `niche-lab:reviewer-ceo`. In the standalone skill, spawn fresh general subagents with the matching file in `prompts/`. For more than 4 niches, one subagent per niche may run phases 3–5 on the shared posting store.
