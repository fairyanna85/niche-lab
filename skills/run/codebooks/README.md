# Codebooks

`core.yml` applies to every niche. Each job family adds one module. A niche uses core + exactly one module; a versatile candidate may have niches in several modules.

Adding a module (rules learned from the reference run, where the codebook was written before reading postings):
1. Collect 15 screen postings for the new family first.
2. List every requirement that appears in ≥3 of them; merge synonyms; drop ones already in core.
3. Write 8–20 codes: `id` (≤10 chars, unique across all modules), `label`, `posting_rule` (what makes it 2, 1, 0), `resume_cues` (regexes, case-insensitive).
4. Code the 15 screen postings with two blind coders; any code with κ <0.6 gets a sharper rule before the module is used.
5. Mark the module `Status: UNTESTED` until a full run with second coding has passed.
