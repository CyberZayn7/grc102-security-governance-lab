# Governance Controls Verification Report

Generated: 2026-10-11T09:57:13+01:00

| Control | Result | Evidence |
|---|---|---|
| Patch management | PASS | Exploit-detection header absent |
| Database authentication | PASS | Former root/password credential rejected |
| Network segmentation | PASS | web=['grc102-security-governance-lab_frontend']; database=['grc102-security-governance-lab_data'] |
| Monitoring | PASS | evidence/post-control/monitoring_snapshot.txt |
| Governance oversight | PASS | 5/5 controls have owners and review dates |

## Conclusion

5 of 5 control categories passed direct verification. Failed tests must be remediated and rerun before the report is submitted.
