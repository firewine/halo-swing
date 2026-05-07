# Review Matrix

Use the smallest review board that fits the risk.

| Work Type | Roles |
| --- | --- |
| Single-file bug or test | owner, QC |
| DTO/schema contract | FE, DB, BE, QC, DevOps, Docs, CTO |
| DB migration/repository | DB, BE, QC, DevOps, Security, Docs, CTO |
| LLM prompt/eval/evidence | AI LLM, Security, QC, BE, Docs, CTO |
| UI/report semantics | FE, BE, QC, Docs, CTO |
| Runtime/cron/watchdog | DevOps, Security, BE, QC, CTO |
| Trading/scoring/risk | AI LLM, BE, QC, Security, CEO, Fintech VC, CTO |
| Release/major refactor | all roles |

Required cross-check pairs:

| Pair | Focus |
| --- | --- |
| FE <-> BE | report contract and API shape |
| BE <-> DB | persistence boundary and replayability |
| BE <-> AI LLM | deterministic code vs hallucination risk |
| Security <-> DevOps | secrets, permissions, runtime safety |
| Security <-> AI LLM | prompt injection and evidence trust |
| QC <-> blocking issue owners | testability |
| Docs <-> CTO | gate truth and stale docs |
| CEO/VC <-> CTO | scope, value, and risk for S4 only |

Do not run all-pairs cross-check unless the user explicitly asks for S4 full
board review.
