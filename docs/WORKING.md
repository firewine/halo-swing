# 작업 메모 (2026-04-27)

> **업데이트**: 작업할 때마다  
> **원칙**: DOING 1개만, RESUME 2줄만  
> **SSOT**: [halo-swing-development-plan.md](./halo-swing-development-plan.md)

---

## DOING (1개만)

- P1 MCP 서버 MVP 준비 — Python 프로젝트 뼈대와 `health_check` MCP 도구 작성 대기

## RESUME (2줄)

1. Halo Swing은 Hermes Agent에 연결되는 시장 스윙 판단 MCP 프로젝트다. 초기 목표는 자동 주문이 아니라 BTC와 지수 2~3배 롱 상품의 매수/손절/익절 가이드, 텔레그램 리포트, 신호 기록과 사후 검증이다.
2. SSOT는 `docs/halo-swing-development-plan.md`이며, 새 대화에서는 `docs/CONTEXT.md`와 이 파일을 먼저 읽으면 프로젝트 맥락을 바로 복구할 수 있다.

---

## 개발 우선순위 로드맵

상세 계획과 계산 근거는 SSOT 문서인 [halo-swing-development-plan.md](./halo-swing-development-plan.md)를 따른다.

### P0 — 프로젝트 기반 정리

| 순서 | 항목 | 레이어 | 상태 |
|------|------|--------|------|
| 1 | GitHub 저장소 생성 및 초기 푸시 | Repo | 완료 |
| 2 | 개발 계획서 작성 | Docs | 완료 |
| 3 | 모든 문서 `docs/` 관리 체계 적용 | Docs | 완료 |
| 4 | `CONTEXT.md` 작성 | Docs | 완료 |
| 5 | `WORKING.md` 작성 | Docs | 완료 |

### P1 — MCP 서버 MVP

| 순서 | 항목 | 레이어 |
|------|------|--------|
| 1 | Python 프로젝트 뼈대 생성 | MCP |
| 2 | MCP 서버 실행 진입점 작성 | MCP |
| 3 | 환경변수와 설정 로딩 | Infra |
| 4 | SQLite 저장소 초기화 | DB |
| 5 | `health_check` 도구 작성 | MCP |

### P2 — 시장 데이터와 지표 엔진

| 순서 | 항목 | 레이어 |
|------|------|--------|
| 1 | OHLCV 수집기 | Data |
| 2 | QQQ/SPY/SMH/SOXX/BTC snapshot | Data |
| 3 | RSI, DMI/ADX, MA, ATR 계산 | Quant |
| 4 | gap/support/resistance 기본 탐지 | Quant |
| 5 | `feature_store` 저장 | DB |

### P3 — 스윙 판단 엔진

| 순서 | 항목 | 레이어 |
|------|------|--------|
| 1 | `score_leverage_swing` 구현 | Quant |
| 2 | `generate_trade_guide` 구현 | Quant |
| 3 | BUY_2X/BUY_3X/WAIT/TRIM/EXIT/STOP 판단 | Quant |
| 4 | 손절/익절/시간손절 가이드 생성 | Risk |

### P4 — 매크로/뉴스/이벤트

| 순서 | 항목 | 레이어 |
|------|------|--------|
| 1 | VIX/VXN/DXY/금리/유가 수집 | Data |
| 2 | FOMC/CPI/PCE/NFP/실적 캘린더 | Event |
| 3 | Fed/Treasury/White House/EIA 뉴스 수집 | News |
| 4 | Iran/유가/AI/반도체 evidence card 생성 | News/LLM |

### P5 — 피드백 파이프라인

| 순서 | 항목 | 레이어 |
|------|------|--------|
| 1 | `signal_ledger` 저장 | DB |
| 2 | Triple Barrier 라벨링 | Quant |
| 3 | MFE/MAE 계산 | Quant |
| 4 | 스코어 캘리브레이션 리포트 | Evaluation |
| 5 | Champion/Challenger 비교 | Evaluation |

### P6 — Hermes 통합

| 순서 | 항목 | 레이어 |
|------|------|--------|
| 1 | Hermes MCP config 예시 작성 | Hermes |
| 2 | 장전/장중/장후 cron prompt | Hermes |
| 3 | 텔레그램 리포트 포맷 | Hermes |
| 4 | 보유 포지션 리뷰 prompt | Hermes |

---

## 현재 미결 문제

1. 실제 MCP 서버 코드는 아직 시작하지 않았다.
2. 데이터 공급원 선택이 필요하다. 초기에는 무료/공식/간단한 소스부터 시작하고 유료 데이터는 인터페이스만 열어둔다.
3. README의 문서 링크가 `docs/` 기준으로 변경됐으므로 GitHub에서 링크 확인이 필요하다.

---

## 최근 완료

- **GitHub 저장소 생성 및 초기 푸시** (2026-04-27)
  - 저장소: `firewine/halo-swing`
  - 로컬 `main` 브랜치를 원격 `origin/main`에 push 완료.
  - 원격 초기 README 커밋과 로컬 계획서 커밋을 병합했다.

- **개발 계획서 작성** (2026-04-27)
  - 최초 개발 계획서를 작성했다.
  - 포함 내용: 개요, 시스템 정의, 아키텍처, 개발 순서, 단계별 상세 개발 계획, 계산 관련 근거.
  - SSOT 문서로 `docs/halo-swing-development-plan.md`에 위치시켰다.

- **문서 체계 정리** (2026-04-27)
  - 모든 문서를 `docs/` 아래에서 관리하도록 정리했다.
  - 새 대화용 핵심 컨텍스트 `docs/CONTEXT.md`를 추가했다.
  - 현재 작업 추적용 `docs/WORKING.md`를 추가했다.
  - README 문서 링크를 `docs/` 기준으로 갱신했다.

- **앱 이름 결정** (2026-04-27)
  - 프로젝트명은 `Halo Swing`.
  - 의미: 위험 경계와 보호막을 보고 스윙 판단을 돕는 개인용 시장 판단 시스템.

---

## 다음 작업 후보

1. Python MCP 프로젝트 스캐폴딩
2. `health_check` MCP 도구 작성
3. SQLite schema 초안 작성
4. QQQ/SPY/BTC 가격 snapshot MVP 작성
5. Hermes MCP config 예시 작성
