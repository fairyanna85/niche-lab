.PHONY: test test-full example reference shots
test:
	python3 -m pytest -q tests
test-full:
	NL_FULL=1 python3 -m pytest -q tests
shots:
	python3 tools/shoot.py /tmp/niche-lab-shots
example:
	./examples/fictional-candidate/rebuild.sh
reference:
	cd reference/partnerships-2026 && python3 analyze.py > /dev/null && python3 then_now.py | head -40 && python3 mh_adjusted.py | head -5

.PHONY: dist agents
agents:
	python3 tools/build_agents.py
dist: agents
	rm -rf dist && mkdir -p dist
	cd skills/run && zip -qr ../../dist/niche-lab-skill.zip . -x "*/__pycache__/*"
