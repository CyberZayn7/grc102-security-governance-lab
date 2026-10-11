.PHONY: check baseline baseline-evidence secure secure-evidence report clean

check:
	docker compose config --quiet
	PYTHONPYCACHEPREFIX=/tmp/grc102-pycache python3 -m py_compile *.py monitoring/*.py
	PYTHONPYCACHEPREFIX=/tmp/grc102-pycache python3 -m unittest -v test_lab.py

baseline:
	docker compose up -d --wait
	mkdir -p evidence/runtime
	docker compose ps > evidence/runtime/docker_ps_baseline.txt
	python3 initialize_governance.py
	python3 vulnerability_scanner.py --mode baseline
	python3 simulate_attack.py
	python3 analyze_governance_failures.py

baseline-evidence:
	python3 capture_evidence.py baseline

secure:
	python3 implement_governance_controls.py --apply
	docker compose down
	docker compose -f docker-compose.secure.yml up -d --wait
	python3 implement_governance_controls.py --verify
	python3 vulnerability_scanner.py --mode post-control
	python3 governance_metrics.py

secure-evidence:
	python3 capture_evidence.py post-control

report:
	python3 build_evidence_report.py

clean:
	docker compose down
	docker compose -f docker-compose.secure.yml down

