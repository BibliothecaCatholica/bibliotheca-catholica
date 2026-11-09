# Test fixtures

`saints-sample.jsonl` is a FIXTURE for `tools/import_saints.py` tests, not site data. Records marked
"(TEST DATA)" are invented on purpose (a prose field, an em-dash, an Amazon link, a bad date, an
outside URL, and a name with no slug) to exercise the importer's checks. The other records use feast
dates from the General Roman Calendar (Agnes Jan 21, Thomas Aquinas Jan 28, Monica Aug 27, Augustine
Aug 28, John Paul II Oct 22, Holy Innocents Dec 28; checked 2026-11-09 against liturgyoffice.org.uk's
General Roman Calendar and the 2014 CDW decree for John Paul II), plus Aquinas's pre-1969 date (Mar 7)
to test merging a slug listed on two days. Their CatholicSaints.Info URLs were not fetched (link-only
rule), so treat them as illustrative.
