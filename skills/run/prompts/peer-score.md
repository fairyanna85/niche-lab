# Prompt — code one person now in the niche's job

Read the public text below (an announcement, a team page or a speaker bio). Output one JSON line:
{"id": "<niche>-pNN", "niche_id": "", "name_hash": "<first 12 hex of sha1(name)>", "source_type": "announcement|team_page|speaker_bio|other",
 "source_url": "", "title": "", "employer": "", "years": <years in the field or null>, "prior_role_type": "<the role held before this one, in a few plain words>",
 "prior_employer_type": "<SaaS vendor | cloud provider | agency or consultancy | start-up | systems integrator | other>",
 "codes": {"<code>": 0 or 1, ...}}
Use the niche's codebook codes. 1 only when the text shows the requirement; absent evidence is 0. Do not store the name in clear text.
TEXT:
{{TEXT}}
