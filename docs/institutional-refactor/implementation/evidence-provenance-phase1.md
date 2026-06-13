# Evidence Provenance Phase 1

## Objective

Create a complete provenance chain without disrupting existing imports.

---

## Current Flow

Import
↓
Trade
↓
Claim

---

## Target Flow

ImportPreviewSession
↓
IngestionSession
↓
ImportBatch
↓
Trade
↓
Claim

---

## Phase 1

Link existing entities.

No EvidenceRecord yet.

---

## Trade Requirements

Populate:

* preview_session_id
* ingestion_session_id
* import_batch_id

during import.

---

## Ingestion Requirements

Create IngestionSession first.

Create ImportBatch second.

Persist Trades third.

Attach IDs during persistence.

---

## Result

Every Trade becomes traceable to:

* Preview Session
* Ingestion Session
* Import Batch

without introducing new infrastructure.
