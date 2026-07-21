# Sprint 1 Retrospective

## Completed
- ETL pipeline: loader, normalizer (21/21 tests pass), validator (16 DQ rules, 1004 failures logged)
- nifty100.db built: 12 tables, FK check = 0 violations
- companies = 92 (AC-01 pass)
- load_audit.csv, validation_failures.csv generated
- Manual review: 5 companies, all pass DQ-16 coverage

## Deviations from doc (flagged, not hidden)
- Doc says "10 tables" / "14 DQ rules" in summary sections but detailed specs (7.1, Section 14) list 12 tables / 16 rules — built to the detailed spec.
- DQ-13 (URL validation) and DQ-15 (INFO-only strict balance) deferred - not blocking, can add later.

## Exit criteria status
All Sprint 1 exit criteria met.