# ImportBatch V2 Proposal

## Objective

Evolve the existing ImportBatch model into a provenance-aware institutional ingestion registry.

This proposal extends the current model rather than replacing it.

---

## Current Responsibilities

ImportBatch currently tracks:

* filename
* rows received
* rows imported
* rows rejected
* import statistics

---

## Future Responsibilities

ImportBatch becomes the canonical ingestion event.

Every import operation creates exactly one ImportBatch.

---

## Future Flow

Broker
↓
Adapter
↓
ImportBatch
↓
EvidenceRecord
↓
Trade
↓
Claim

---

## Proposed Additional Fields

source_type

adapter_name

broker_name

account_identifier

source_checksum

source_hash

import_mode

verification_state

source_metadata_json

ingested_at

completed_at

---

## Verification States

pending

processing

completed

verified

failed

---

## Compatibility Requirement

Existing imports:

* CSV
* MT5
* IBKR

must continue using ImportBatch.

No ingestion workflow may be broken.

---

## Institutional Benefits

* Provenance
* Auditability
* Import tracing
* Evidence lineage
* Broker verification support
