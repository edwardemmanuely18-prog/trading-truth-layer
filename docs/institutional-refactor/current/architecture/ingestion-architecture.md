# Current TTL Ingestion Architecture

## Objective

Document the current ingestion architecture before institutional refactoring begins.

This document reflects the production ingestion flow as implemented today.

---

## Current Sources

TTL currently supports:

* Manual Trade Entry
* CSV Upload
* MT5 Export Upload
* IBKR Export Upload

---

## Current Processing Flow

Source File
↓
trade_import.py
↓
normalize_trade()
↓
validate_trade()
↓
process_import_rows()
↓
persist_runtime_trade_rows()
↓
Trade Ledger
↓
Claim Engine
↓
Public Trust Layer

---

## Current Components

### trade_import.py

Responsibilities:

* Source detection
* MT5 mapping
* IBKR mapping
* CSV mapping
* Normalization
* Validation
* Fingerprinting

### ingestion_service.py

Responsibilities:

* Import session creation
* Import batch tracking
* Persistence
* Duplicate protection
* Statistics generation

---

## Existing Strengths

* Fingerprint generation
* Duplicate detection
* Import tracking
* Source detection
* Lifecycle compatibility

---

## Existing Limitations

Current architecture persists directly into Trade records.

Missing institutional layers:

* Evidence Registry
* Evidence Records
* Provenance Layer
* Verification Events
* Integrity Monitoring

---

## Current Canonical Flow

Import
↓
Trade
↓
Claim
↓
Public Record

This architecture remains operational and must remain functional during all refactor phases.
