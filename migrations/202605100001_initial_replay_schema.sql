CREATE TABLE IF NOT EXISTS schema_migrations (
    version TEXT PRIMARY KEY,
    checksum TEXT NOT NULL,
    applied_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS strategy_config (
    config_hash TEXT PRIMARY KEY,
    schema_version TEXT NOT NULL DEFAULT 'strategy_config.v1',
    config_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS run_journal (
    run_id TEXT PRIMARY KEY,
    idempotency_key TEXT UNIQUE,
    run_type TEXT NOT NULL,
    status TEXT NOT NULL,
    started_at TEXT NOT NULL,
    completed_at TEXT,
    metadata_json TEXT NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS feature_store (
    feature_snapshot_id TEXT PRIMARY KEY,
    asset TEXT NOT NULL,
    underlying TEXT NOT NULL,
    timeframe TEXT NOT NULL,
    created_at TEXT NOT NULL,
    features_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS evidence_card (
    evidence_id TEXT PRIMARY KEY,
    modality TEXT NOT NULL,
    summary TEXT NOT NULL,
    source_ref TEXT,
    created_at TEXT NOT NULL,
    payload_json TEXT NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS artifact_ref (
    artifact_ref_id TEXT PRIMARY KEY,
    ref_type TEXT NOT NULL,
    ref TEXT NOT NULL,
    metadata_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS signal_ledger (
    signal_id TEXT PRIMARY KEY,
    created_at TEXT NOT NULL,
    asset TEXT NOT NULL,
    underlying TEXT NOT NULL,
    timeframe TEXT NOT NULL,
    action TEXT NOT NULL,
    final_score REAL NOT NULL,
    confidence REAL NOT NULL,
    data_freshness_status TEXT NOT NULL,
    run_id TEXT NOT NULL,
    feature_snapshot_id TEXT NOT NULL,
    config_hash TEXT NOT NULL,
    evidence_card_ids_json TEXT NOT NULL DEFAULT '[]',
    artifact_ref_ids_json TEXT NOT NULL DEFAULT '[]',
    signal_json TEXT NOT NULL,
    FOREIGN KEY (run_id) REFERENCES run_journal (run_id),
    FOREIGN KEY (feature_snapshot_id) REFERENCES feature_store (feature_snapshot_id),
    FOREIGN KEY (config_hash) REFERENCES strategy_config (config_hash)
);

CREATE TABLE IF NOT EXISTS label_store (
    label_id TEXT PRIMARY KEY,
    signal_id TEXT NOT NULL,
    outcome TEXT NOT NULL,
    labeled_at TEXT NOT NULL,
    horizon_days INTEGER,
    label_json TEXT NOT NULL,
    FOREIGN KEY (signal_id) REFERENCES signal_ledger (signal_id)
);

CREATE INDEX IF NOT EXISTS idx_signal_ledger_created_at
    ON signal_ledger (created_at);
CREATE INDEX IF NOT EXISTS idx_signal_ledger_asset
    ON signal_ledger (asset);
CREATE INDEX IF NOT EXISTS idx_signal_ledger_underlying
    ON signal_ledger (underlying);
CREATE INDEX IF NOT EXISTS idx_signal_ledger_timeframe
    ON signal_ledger (timeframe);
CREATE INDEX IF NOT EXISTS idx_signal_ledger_action
    ON signal_ledger (action);
CREATE INDEX IF NOT EXISTS idx_signal_ledger_config_hash
    ON signal_ledger (config_hash);
CREATE INDEX IF NOT EXISTS idx_signal_ledger_data_freshness_status
    ON signal_ledger (data_freshness_status);
CREATE INDEX IF NOT EXISTS idx_feature_store_asset
    ON feature_store (asset);
CREATE INDEX IF NOT EXISTS idx_feature_store_underlying
    ON feature_store (underlying);
CREATE INDEX IF NOT EXISTS idx_feature_store_timeframe
    ON feature_store (timeframe);
CREATE INDEX IF NOT EXISTS idx_run_journal_status
    ON run_journal (status);
CREATE INDEX IF NOT EXISTS idx_label_store_signal_id
    ON label_store (signal_id);
CREATE INDEX IF NOT EXISTS idx_label_store_outcome
    ON label_store (outcome);
