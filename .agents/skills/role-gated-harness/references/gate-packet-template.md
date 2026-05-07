# Gate Packet Template

~~~md
# <GATE_ID>

## Gate Result

```yaml
call: GO | NO_GO | CHANGE_REQUEST
gate_id: <GATE_ID>
review_tier: S1_small | S2_medium | S3_architecture_gate | S4_product_or_risk_gate
mode_after_gate: implement | gate_plan | diff_review | repair
recommendation: ...
```

## Approved Scope

- ...

## Blocked Scope

- ...

## Implementation Order

1. ...

## Required Verification

```bash
...
```

## No-Go Conditions

- ...

## Review Sources

- `docs/reviews/<GATE_ID>/...`

## CTO Decision

Short synthesis only. Do not paste every role review here.
~~~

Task contract must include:

```json
{
  "gate_id": "<GATE_ID>",
  "mode": "implement",
  "review_tier": "S1_small",
  "source_gate_packet": "docs/gates/<GATE_ID>.md",
  "next_atomic_step": "...",
  "allowed_edit_paths": [],
  "read_only_context": [],
  "blocked_path_prefixes": [],
  "blocked_exact_paths": [],
  "required_commands": [],
  "post_implementation_review": {
    "roles": [],
    "rounds": 1,
    "read_only": true
  },
  "done_means": [],
  "next_state_after_success": "..."
}
```
