# GRC102 Security Governance Simulation

Practical Lab 8 demonstrates how technical evidence supports patching, monitoring, segmentation, database security, accountability, metrics, and executive oversight. It follows the official ICDFA Week 8 lab structure while making the before/after tests deterministic and evidence based.

> **Authorised scope:** Run only on a local or ICDFA-provided isolated Docker environment. Do not target public, organisational, or third-party systems. All included customer records are synthetic.

## Architecture

The baseline places an intentionally vulnerable Struts service, MySQL database, and monitoring container on one shared network. The controlled configuration replaces the vulnerable service, uses unique local secrets, removes database host exposure, and separates frontend and internal data networks. The monitoring container alone joins both networks.

## Prerequisites

- Docker Desktop or Docker Engine with Compose
- Python 3.9 or newer
- Google Chrome at the standard macOS application path for automated evidence screenshots and PDF generation
- About 4 GB of free disk space for legacy training images

Legacy baseline images use `linux/amd64` emulation when required. The web port is bound to `127.0.0.1` and is not exposed to the external network.

The current Vulhub manifest maps S2-045 to `vulhub/struts2:2.3.30`; the obsolete `s2-045` image tag printed in the course handout is not available from the registry.

## Run the assessment

```bash
make check
make baseline
make baseline-evidence
make secure
make secure-evidence
make report
```

Review every command result. A non-zero control verification result must be fixed and rerun rather than hidden.

### Equivalent baseline commands

```bash
docker compose up -d --wait
docker compose ps
python3 initialize_governance.py
python3 vulnerability_scanner.py --mode baseline
python3 simulate_attack.py
python3 analyze_governance_failures.py
python3 capture_evidence.py baseline
```

### Equivalent control commands

```bash
python3 implement_governance_controls.py --apply
docker compose down
docker compose -f docker-compose.secure.yml up -d --wait
python3 implement_governance_controls.py --verify
python3 vulnerability_scanner.py --mode post-control
python3 governance_metrics.py
python3 capture_evidence.py post-control
python3 build_evidence_report.py --student-name "Zainab Umar Shuaibu" --student-id "C11/26/CGRCE/17194"
```

## Evidence index

| Requirement | Evidence |
|---|---|
| Environment and initialisation | `docker-compose.yml`, `database_init/init.sql`, `governance_dashboard.html` |
| Baseline vulnerability evidence | `evidence/baseline/` |
| Safe simulation | `attack_log.json` |
| Governance failures and Equifax comparison | `evidence/baseline/`, `equifax_comparison.md` |
| Implemented controls | `docker-compose.secure.yml`, `patch_status.json`, `governance_oversight.md` |
| Verification | `controls_report.md`, `evidence/post-control/` |
| Metrics and reporting | `executive_dashboard.html`, `board_report.md`, `metrics_framework.md`, `dashboard_user_guide.md` |
| Labelled visual evidence | `evidence/screenshots/` |
| Associated report | `GRC102_Lab8_Evidence_Report.pdf` |

## Control-to-failure mapping

| Failure | Control | Direct verification |
|---|---|---|
| Unpatched Struts component | Vulnerable service replacement and critical patch SLA | S2-045 response header is absent |
| Default database authentication | Generated local secrets and least-privilege account | Former `root/password` login is rejected |
| Shared application/database network | Separate frontend and internal data networks | Docker network memberships have no intersection |
| Ineffective monitoring | Dated service and web-log snapshot | Monitoring evidence file is generated |
| Weak accountability | Named owners, review dates, targets, and escalation | All five control categories have ownership evidence |

## Cleanup

```bash
make clean
```

Volumes are retained so evidence can be reproduced. Delete them only after assessment evidence is safely retained:

```bash
docker compose down -v
docker compose -f docker-compose.secure.yml down -v
```

## References

- [ICDFA GRC102 Week 8 Lab Instructions](https://github.com/icdfa/grc-engineering-labs/blob/master/phase1/grc102/week8/LAB_INSTRUCTIONS.md)
- [NIST NVD: CVE-2017-5638](https://nvd.nist.gov/vuln/detail/CVE-2017-5638)
- U.S. GAO, *Data Protection: Actions Taken by Equifax and Federal Agencies in Response to the 2017 Breach*, GAO-18-559 (2018)
- U.S. House Committee on Oversight and Government Reform, *The Equifax Data Breach* (2018)

## Academic integrity

This repository is an assessment aid, not a substitute for the learner's own work. The submitting learner must understand the implementation, verify the report details, acknowledge assistance and sources as required by course policy, and never present generated or unverified output as observed fact.

