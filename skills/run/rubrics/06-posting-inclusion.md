# Rubric 06 — Posting inclusion

Include a posting only if ALL hold:
1. Title matches the module `title_patterns` and the niche level band (±1 band).
2. City matches the niche city, or remote explicitly open to that city's country.
3. Full description text ≥120 words is stored in `postings/raw/<sha256>.txt`.
4. Date evidence exists (posted date, "x days ago" with capture date, removal stamp, or an in-text year anchor for archives).
5. Not a duplicate: same company + normalized title + city within 60 days = one posting (keep the employer/ATS copy).

Source priority when the same job appears twice: employer careers page / ATS (Greenhouse, Lever, Ashby, Workday) > aggregator mirror (Built In, Indeed, ZipRecruiter) > agency post.
Exclude internships, temp contracts under 6 months, and postings in a language the niche city does not use.
Archive postings (closed, for then-vs-now) must have a removal stamp or a dated listing page; era = year of the evidence.
Target per kept niche: ≥30 "now" postings (statistical tests switch on at 30) and ≥15 archive postings across two eras.
