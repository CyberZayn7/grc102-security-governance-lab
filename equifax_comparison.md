# Equifax Comparison and Governance Lessons

## Comparison

The isolated simulation models governance conditions associated with the 2017 Equifax breach without recreating harm or accessing real information. Both cases centre on a known Apache Struts vulnerability, delayed remediation, gaps between written policy and implementation, inadequate visibility, weak accountability, and architecture that allowed the effect of a web-tier compromise to expand.

The simulation is intentionally limited. It contains three synthetic customer rows, performs only a response-header detection request, and records a hypothetical attack event. It does not reproduce Equifax's scale, production complexity, duration, certificate-monitoring problem, or impact on real individuals. Its results therefore demonstrate control behaviour, not the probability or financial impact of a real breach.

## Key governance lessons

1. Critical vulnerability notices require a named owner, deadline, confirmation, and escalation—not only an email or policy.
2. Independent verification is needed because deployment reports can be incomplete or incorrect.
3. Segmentation and least privilege limit the consequences of an application compromise.
4. Monitoring coverage is a governance concern: executives need to know which critical assets are invisible.
5. Board metrics should expose overdue risk and decisions required, rather than merely count activity.

## References

- U.S. Government Accountability Office, *Data Protection: Actions Taken by Equifax and Federal Agencies in Response to the 2017 Breach*, GAO-18-559 (2018).
- U.S. House Committee on Oversight and Government Reform, *The Equifax Data Breach* (2018).
- NIST National Vulnerability Database, CVE-2017-5638.
- ICDFA, *GRC102 Week 8 Lab Instructions*.

