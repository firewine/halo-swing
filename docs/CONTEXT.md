# Halo Swing Development Context

> 역할: 새 대화와 개발 작업 시작 시 항상 먼저 읽는 짧은 핵심 컨텍스트  
> 대상: 사용자, 개발자, Hermes Agent, Codex, QA  
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

### Harness Engineering

- 새 기능은 가능한 한 작은 실행 하네스와 함께 만든다.
- 각 MCP 도구는 Hermes 없이도 CLI/test에서 단독 실행 가능해야 한다.
- 외부 API, 뉴스, LLM 응답은 fixture/replay 모드로 고정 재현할 수 있어야 한다.
- market data, indicator, scoring, labeling, report 각각에 golden fixture를 둔다.
- 하네스는 구현 편의가 아니라 다음 LLM이 안전하게 수정하기 위한 작업 발판이다.

### Virtual Team Gates

Codex에 지속형 멀티에이전트 개발팀이 없더라도, 작업은 아래 역할 게이트를 통과한 것으로 기록한다.

- Dev: 기능 구현, 최소 하네스, 단위 테스트를 만든다.
- QC: fixture/golden/live-smoke를 분리해 재현성과 회귀를 확인한다.
- CTO: 아키텍처, 과최적화, 리스크 예산, 자동주문 범위 침범 여부를 본다.
- Docs Gardener: SSOT, CONTEXT, WORKING이 현재 구현과 어긋나지 않게 정리한다.

역할은 실제 별도 에이전트일 필요는 없다. 한 LLM 세션에서 수행하더라도 산출물과 체크는 분리한다.

## 4. What To Read Before Work

작업 시작 전 최소 확인 순서:

1. 이 문서
2. [WORKING.md](./WORKING.md)
3. [halo-swing-development-plan.md](./halo-swing-development-plan.md)

항상 모든 내용을 다 읽을 필요는 없다. 현재 작업과 직접 관련된 섹션만 좁게 읽는다.

## 5. Document System

```text
docs/
  CONTEXT.md
    - 새 대화와 개발 시작용 짧은 프로젝트 헌법

  WORKING.md
    - 현재 DOING 1개, RESUME, 우선순위, 최근 완료

  halo-swing-development-plan.md
    - SSOT 개발 계획서
    - 시스템 정의, 아키텍처, 단계별 계획, 계산 근거
```

## 6. Initial Product Shape

초기 제품은 다음 MCP 도구를 제공한다.

```text
get_market_snapshot
get_macro_snapshot
get_event_calendar
get_news_bundle
calculate_indicators
render_chart
score_leverage_swing
generate_trade_guide
evaluate_position
record_signal
label_signal_outcome
evaluate_score_performance
compare_champion_challenger
```

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
- Dev/QC/CTO/Docs Gardener 관점의 gate가 분리되어 있는가?
- 매수 신호에 손절/익절 조건이 포함되는가?
- 신호 기록과 사후 라벨링 경로가 있는가?
- 레버리지 ETF의 일일 리셋/변동성 drag를 고려했는가?
- 자동 주문이 MVP 범위를 침범하지 않았는가?
