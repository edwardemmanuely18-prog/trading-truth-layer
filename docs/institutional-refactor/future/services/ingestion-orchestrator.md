# Ingestion Orchestrator

## Problem

Current ingestion creates:

- Trades
- ImportBatch
- IngestionSession

independently.

There is no single ingestion workflow owner.

---

## Future Architecture

ImportPreviewSession
↓
IngestionSession
↓
ImportBatch
↓
Trade
↓
EvidenceRecord

---

## Responsibilities

Create ingestion session

Create import batch

Persist trades

Persist evidence records

Generate audit events

Generate provenance chain

---

## Design Goal

Every import operation should have one orchestrator.

Adapters should normalize data.

Orchestrator should persist data.

---

## Benefits

Single ingestion workflow

Broker integrations become simpler

Evidence provenance becomes traceable

Integrity monitoring becomes possible