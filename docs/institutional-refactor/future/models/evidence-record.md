# EvidenceRecord Model Proposal

## Purpose

Create an immutable evidence layer between Import Batch and Trade Ledger.

---

## Future Flow

Import Batch
↓
EvidenceRecord
↓
Trade

---

## Proposed Fields

id

workspace_id

import_batch_id

source_type

adapter_name

source_identifier

verification_state

evidence_hash

trade_fingerprint

raw_payload_json

normalized_payload_json

ingested_at

created_at

---

## Verification States

pending

validated

verified

rejected

---

## Notes

EvidenceRecord is not a replacement for Trade.

EvidenceRecord becomes the provenance layer that proves where Trade records originated.

Trade remains the canonical operational ledger.
