# Prompt — blind panel: which resume would you call?

You are three readers in turn: a recruiter screening for the role, the hiring manager, and the executive the role reports to.
You see two resumes of the same person, labelled A and B. You are not told which is newer; do not guess, judge only what is on the page.
The role: {{NICHE}}.

For each reader, score A and B from 1 to 10 on "would I take the call", choose one, and give one sentence why.
Output JSON only:
{"reviewers": [{"reviewer": "recruiter", "A": n, "B": n, "chose": "A"|"B", "why": ""}, {"reviewer": "hiring manager", ...}, {"reviewer": "executive", ...}],
 "independent": false, "note": "three readers played in one session"}
A:
{{A}}
B:
{{B}}
