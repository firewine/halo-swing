"""DTO contracts for Halo Swing reports and replay bundles."""

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class StrictBaseModel(BaseModel):
    """Base DTO that rejects accidental contract drift."""

    model_config = ConfigDict(extra="forbid")


class TradeAction(StrEnum):
    BUY_2X = "BUY_2X"
    BUY_3X = "BUY_3X"
    WAIT = "WAIT"
    TRIM = "TRIM"
    EXIT = "EXIT"
    STOP = "STOP"


class DataFreshnessStatus(StrEnum):
    FRESH = "FRESH"
    STALE = "STALE"
    PARTIAL = "PARTIAL"
    UNKNOWN = "UNKNOWN"


class SignalStatus(StrEnum):
    GENERATED = "GENERATED"
    DEGRADED = "DEGRADED"
    ERROR = "ERROR"


class ArtifactRefType(StrEnum):
    CHART = "CHART"
    PDF = "PDF"
    NEWS = "NEWS"
    EXTERNAL = "EXTERNAL"
    OTHER = "OTHER"


class ReplayErrorCode(StrEnum):
    MISSING_REQUIRED_LINK = "MISSING_REQUIRED_LINK"
    INCOMPLETE_REPLAY_BUNDLE = "INCOMPLETE_REPLAY_BUNDLE"


class ArtifactRef(StrictBaseModel):
    ref_type: ArtifactRefType
    ref: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class ReplayMissingLinkError(StrictBaseModel):
    code: ReplayErrorCode
    message: str
    missing_ref_type: str
    missing_ref_id: str | None = None


class LatestSignalReport(StrictBaseModel):
    signal_id: str
    created_at: str
    asset: str
    underlying: str
    timeframe: str
    action: TradeAction
    action_label: str
    final_score: float
    confidence: float = Field(ge=0, le=1)
    entry_summary: str
    stop_summary: str
    take_profit_summary: str
    invalidation_summary: str
    risk_summary: str
    data_freshness_status: DataFreshnessStatus
    degraded_mode: bool
    data_warnings: list[str]
    config_hash: str
    reason_summary: str | None = None
    evidence_summary: str | None = None
    label_status: str | None = None
    chart_ref: ArtifactRef | None = None


class SignalReplayBundle(StrictBaseModel):
    signal: dict[str, Any]
    feature_snapshot: dict[str, Any]
    evidence_cards: list[dict[str, Any]]
    strategy_config: dict[str, Any]
    run_journal: dict[str, Any]
    label_outcome: dict[str, Any] | None = None
    missing_links: list[ReplayMissingLinkError]


class StorageHealth(StrictBaseModel):
    status: str
    driver: str
    database_kind: str
    migration_count: int
    latest_migration: str | None
    domain_tables_present: list[str]
    live_data_required: bool


__all__ = [
    "ArtifactRef",
    "ArtifactRefType",
    "DataFreshnessStatus",
    "LatestSignalReport",
    "ReplayErrorCode",
    "ReplayMissingLinkError",
    "SignalReplayBundle",
    "SignalStatus",
    "StorageHealth",
    "TradeAction",
]
