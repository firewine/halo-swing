# Harness Promotion And Metrics

Role-based cross-check is an inferential harness layer. Keep it for medium and
large changes, but promote repeated findings into deterministic controls.

## Promotion Rule

If the same role finding appears twice, promote it to one of:

- test
- hook
- rule
- linter or security scan
- `AGENTS.md` rule
- skill instruction
- ADR
- backlog item

## Promotion Examples

| Finding | Promotion |
| --- | --- |
| Scope drift | Stop hook and task contract |
| Risky shell command | `.codex/rules` or PreToolUse hook |
| Fixture local path | pytest path scan |
| Secrets leak | detect-secrets or security scan |
| Dependency risk | pip-audit or dependency gate |
| Python security smell | Bandit or Semgrep |
| Import boundary drift | architecture test |
| LLM numeric authority | contract test or eval |
| Stale docs | docs freshness check |

## Useful Metrics

Track these for S2 or higher work when practical:

```yaml
quality_metrics:
  review:
    - role_review_findings_count
    - blocking_findings_count
    - findings_accepted_rate
    - duplicate_findings_rate
    - false_positive_rate
  code:
    - post_merge_bug_count
    - revert_count
    - changed_lines_per_task
    - test_count_added
    - coverage_delta
  security:
    - security_findings_by_stage
    - secrets_detected
    - dependency_vulns
    - prompt_injection_test_failures
  harness:
    - findings_promoted_to_tests
    - findings_promoted_to_hooks
    - findings_promoted_to_rules
    - scope_violations_blocked
    - verification_failures_caught_before_finish
  cost:
    - token_cost_per_gate
    - token_cost_per_blocker_found
    - review_tier_distribution
```
