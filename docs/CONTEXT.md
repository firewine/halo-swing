# Halo Swing Development Context

> 역할: 새 대화와 개발 작업에서 필요할 때 참고하는 짧은 핵심 컨텍스트
> 대상: 사용자, 개발자, DevOps, Hermes Agent, Codex, QA
> 업데이트: 프로젝트 정의나 운영 원칙이 바뀔 때만
> 버전: v0.1 (2026-04-27)

## 목적

Halo Swing은 Hermes Agent에 연결할 개인용 시장 스윙 판단 MCP 프로젝트다.

목표는 BTC와 미국 지수 2~3배 롱 상품을 대상으로 다음 질문에 답하는 것이다.

- 지금 스윙 매수 후보인가?
- 산다면 2배가 맞는가, 3배가 맞는가?
- 진입 논리가 깨지는 손절 조건은 무엇인가?
- 익절 또는 일부 청산 조건은 무엇인가?
- 보유 중이라면 유지, 축소, 청산 중 무엇이 맞는가?
- 과거 비슷한 신호는 실제로 어떻게 됐는가?

초기 목표는 자동 주문이 아니라 **판단 보조, 텔레그램 리포트, 신호 기록, 사후 검증**이다.

## 1. SSOT

- 개발 계획과 시스템 정의의 유일한 정본은 [halo-swing-development-plan.md](./halo-swing-development-plan.md)다.
- 요구사항, 아키텍처, 계산 근거를 다른 문서에 중복 복제하지 않는다.
- 새 문서는 `docs/` 아래에만 둔다.
- 문서가 길어질 경우에도 핵심 변경은 먼저 SSOT에 반영한다.

## 2. System Definition

```text
Hermes Agent
  - Codex OAuth 또는 다른 LLM provider
  - 대화, 텔레그램, 크론, 메모리
  - 최종 설명과 판단 요약

Halo Swing MCP
  - 가격/매크로/뉴스/이벤트 데이터 수집
  - 지표 계산
  - 스윙 신호 계산
  - 매수/손절/익절 가이드 생성
  - 신호 기록과 결과 라벨링
  - 스코어링 피드백 계산
```

## 3. Non-Negotiables

### Calculation

- 숫자 계산은 MCP 서버 코드가 한다.
- LLM은 자료 해석, 충돌 판단, 설명 생성에 사용한다.
- 차트 이미지만 보고 RSI, DMI, 손절가를 추정하지 않는다.
- 지표값은 OHLCV 데이터에서 계산한다.

### Trading Scope

- 레버리지 ETF는 장기 보유 자산이 아니라 스윙 전술 자산이다.
- QLD/TQQQ는 QQQ/NDX 기준으로 판단한다.
- SSO/UPRO는 SPY/SPX 기준으로 판단한다.
- SOXL은 SMH/SOXX/SOX와 주요 반도체 주도주 기준으로 판단한다.
- BTC는 BTC spot/futures, funding, OI, 매크로 리스크를 함께 본다.

### Risk

- 매수 신호는 손절 조건과 익절 조건 없이 출력하지 않는다.
- 신규 롱 금지, 관망, 축소, 청산 판단도 매수 판단만큼 중요하다.
- 자동 주문은 MVP 범위가 아니다.
- 주문 연동을 하더라도 승인 기반 수동 실행을 기본값으로 둔다.

### Feedback

- 모든 신호는 `signal_ledger`에 기록한다.
- 신호는 Triple Barrier 방식으로 사후 라벨링한다.
- 스코어 변경은 Champion/Challenger 방식으로 검증한다.
- 자동 개선안은 제안까지만 하고, 실사용 반영은 검증 후 한다.
- 모든 신호는 어떤 가중치/임계값 설정으로 생성됐는지 추적 가능해야 한다.
- 가중치 JSON은 버전과 해시를 갖고, feedback pipeline은 active 설정을 자동 덮어쓰지 않는다.

### Runtime State

- 장기 실행 프로세스는 run journal, checkpoint, watchdog event를 남긴다.
- 메모리 덤프와 runtime artifact는 git에 커밋하지 않는다.
- watchdog는 메모리 한계, 큐 적체, 반복 오류, 비정상 값 증가를 감시한다.
- 복구 가능한 상태와 재현용 입력 snapshot은 구분해서 저장한다.
- 24/7 운영은 내부 watchdog만 믿지 않고 외부 supervisor/restart 정책도 둔다.
- 모든 live 작업은 timeout, retry limit, circuit breaker, idempotency key를 가져야 한다.
- 큐, 캐시, evidence bundle, 로그, checkpoint는 크기와 보존 기간을 제한한다.
- 오류가 반복되면 자동 매수/리포트 생성을 계속 밀어붙이지 않고 degraded mode로 전환한다.

### Harness Engineering

- 새 기능은 가능한 한 작은 실행 하네스와 함께 만든다.
- 각 MCP 도구는 Hermes 없이도 CLI/test에서 단독 실행 가능해야 한다.
- 외부 API, 뉴스, LLM 응답은 fixture/replay 모드로 고정 재현할 수 있어야 한다.
- market data, indicator, scoring, labeling, report 각각에 golden fixture를 둔다.
- 하네스는 구현 편의가 아니라 다음 LLM이 안전하게 수정하기 위한 작업 발판이다.

### Virtual Team Gates

Codex에 지속형 멀티에이전트 개발팀이 없더라도, 작업은 아래 역할 게이트를 통과한 것으로 기록한다.

- Dev: 기능 구현, 최소 하네스, 단위 테스트를 만든다.
- DevOps: 개발 환경, 의존성, 실행 명령, Hermes MCP 연결 설정을 관리한다.
- QC: fixture/golden/live-smoke를 분리해 재현성과 회귀를 확인한다.
- CTO: 아키텍처, 과최적화, 리스크 예산, 자동주문 범위 침범 여부를 본다.
- Docs Gardener: SSOT, CONTEXT, WORKING이 현재 구현과 어긋나지 않게 정리한다.

역할은 실제 별도 에이전트일 필요는 없다. 한 LLM 세션에서 수행하더라도 산출물과 체크는 분리한다.

## 4. What To Read Before Work

agent runner의 첫 운영 규칙은 repository root의 [AGENTS.md](../AGENTS.md)다.
일반 구현 작업에서는 [WORKING.md](./WORKING.md)를 active contract로 먼저 읽고,
그 안의 `read_only_context`가 지정한 SSOT 또는 CONTEXT 구간만 좁게 읽는다.

[halo-swing-development-plan.md](./halo-swing-development-plan.md)는 durable SSOT지만,
구현 작업마다 전문을 읽지 않는다. 현재 작업 계약이 요구하는 섹션만 확인한다.

## 5. Document System

```text
docs/
  CONTEXT.md
    - 새 대화와 개발 시작용 짧은 프로젝트 헌법

  WORKING.md
    - 현재 DOING 1개, RESUME, 우선순위, 최근 완료

  devops-setup-guide.md
    - 로컬 개발환경, 의존성 설치, Hermes MCP 연결 설정

  halo-swing-development-plan.md
    - SSOT 개발 계획서
    - 시스템 정의, 아키텍처, 단계별 계획, 계산 근거
```

## 6. Current Product Shape

현재 MCP tool surface의 권위 있는 목록은 `health_check`와
`tests/golden/health_check.json`의 `capabilities`다. 이 문서는 전체 manifest를
복제하지 않고 현재 MVP 계열만 요약한다.

```text
core market context
  - market, macro, events, news, evidence card, indicators, chart

swing decision and reporting
  - score, trade guide, position review, latest signal report, cron prompt pack

recording, replay, and feedback
  - record signal, label outcome, evaluate performance, replay bundle,
    weight suggestion, champion/challenger comparison

integration and live-smoke harnesses
  - readiness, setup checklist, API-key status, provider route,
    live-data smoke validation, integration/API-key pipeline smokes

audit, runtime, and guarded BTC operations
  - audit summary, runtime status/checkpoint, BTC risk settings/status,
    Binance credential/connectivity/account snapshot normalization,
    BTC order preview and confirmation-gated execution tool
```

자동 주문, broker/order submission, Hermes runtime start, Telegram send,
scheduler, live adapter 확장, `.env` 기반 DB 자동 활성화는 별도 gate 승인 전까지
제품 범위로 보지 않는다.

최종 출력 액션:

```text
BUY_3X
BUY_2X
BUY_WATCH
WAIT
TRIM
EXIT
STOP
BLOCK
```

## 7. Quick Checklist

- 문서가 `docs/` 밖에 생기지 않았는가?
- SSOT 내용을 중복 복제하지 않았는가?
- 계산 로직을 LLM에게 맡기지 않았는가?
- 새 기능을 검증할 실행 하네스나 fixture가 있는가?
- Dev/DevOps/QC/CTO/Docs Gardener 관점의 gate가 분리되어 있는가?
- 로컬 실행 명령과 Hermes 설정이 DevOps 가이드에 반영되어 있는가?
- 매수 신호에 손절/익절 조건이 포함되는가?
- 신호 기록과 사후 라벨링 경로가 있는가?
- 가중치/임계값 설정의 version/hash가 신호와 연결되는가?
- 장기 실행 시 checkpoint와 watchdog 기준이 있는가?
- 레버리지 ETF의 일일 리셋/변동성 drag를 고려했는가?
- 자동 주문이 MVP 범위를 침범하지 않았는가?
