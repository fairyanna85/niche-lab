#!/usr/bin/env python3
"""Generate agents/*.md from skills/run/prompts/*.md so the plugin's subagents and the standalone prompts never drift."""
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
DESC = {
    "second-coder": "Blind second coder for niche-lab. Codes job postings against the given codebook without seeing the first coder's work. Use only when niche-lab's run skill asks for reliability coding.",
    "advocate": "niche-lab advocate test. Reads only the top third of a resume once and says in one sentence who the person is. Use only when niche-lab's run skill asks for the advocate test.",
    "reviewer-recruiter": "niche-lab recruiter reviewer. Scores a niche resume on keywords and scope clarity and lists red flags. Use only inside niche-lab's review loop.",
    "reviewer-hiring-manager": "niche-lab hiring-manager reviewer. Scores relevance, proof and level fit for a niche resume. Use only inside niche-lab's review loop.",
    "reviewer-ceo": "niche-lab adversarial CEO reviewer. Says 'Good job' or 'Not yet' with at most 8 fixes. Use only inside niche-lab's review loop.",
}
for name, desc in DESC.items():
    prompt = (ROOT / "skills" / "run" / "prompts" / f"{name}.md").read_text().strip()
    body = (f"---\nname: {name}\ndescription: {desc}\ntools: Read\n---\n\n"
            "You are a fresh, independent reviewer. You have not seen any other agent's output for this task. "
            "Return only the output format the prompt asks for.\n\n" + prompt + "\n")
    (ROOT / "agents" / f"{name}.md").write_text(body)
    print("wrote agents/" + name + ".md")
