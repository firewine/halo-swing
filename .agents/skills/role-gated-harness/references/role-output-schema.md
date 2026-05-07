# Role Output Schema

Use this schema for role reviews.

```yaml
role: DB
decision: READY | BLOCKED | CHANGE_REQUEST
scope_view:
  allowed:
    - ...
  forbidden:
    - ...
blocking_issues:
  - id: DB-BLOCK-001
    severity: high
    issue: ...
    evidence: ...
    required_change: ...
nonblocking_issues:
  - id: DB-NB-001
    issue: ...
required_tests_or_guards:
  - ...
files_at_risk:
  - ...
harness_promotion_candidates:
  - target: test | hook | rule | linter | security_scan | AGENTS | skill | ADR | backlog
    reason: ...
handoff_to:
  - BE
  - QC
```

Round 2 is blocker closure only:

```yaml
round_2:
  unresolved_blockers:
    - id: SECURITY-BLOCK-002
      status: unresolved
      reason: ...
  resolved_blockers:
    - id: QC-BE-001
      resolution: ...
  new_blockers_allowed: true
  new_nonblocking_issues_allowed: false
```

Diff review output:

```yaml
role: qc
blocking_findings:
  - id: QC-DIFF-001
    finding_type: missing_test
    evidence: ...
    required_change: ...
nonblocking_findings: []
missing_tests: []
harness_promotion_candidates:
  - target: stop_hook | rule | test | AGENTS | skill | ADR | backlog
    reason: ...
```
