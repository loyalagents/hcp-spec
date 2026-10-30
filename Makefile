DRAFT ?= 2.0-draft-2
SPEC = spec/$(DRAFT)
SCHEMAS = schemas/$(DRAFT)
HEADER ?= Human Context Protocol (HCP) v2  |  Draft Specification  |  October 2026

.PHONY: schemas check docx

schemas:
	python3 -I tools/make_schemas.py $(SCHEMAS) $(DRAFT)

check: schemas
	python3 -I tools/check_schemas.py $(SCHEMAS) $(SPEC)

docx:
	mkdir -p out
	for f in title_clean.md $$(for n in $$(seq 1 27); do printf 's%s.md ' $$n; done); do cat $(SPEC)/$$f; printf '\n'; done > out/$(DRAFT).md
	python3 -I tools/build.py template/template.docx out/$(DRAFT).md "out/Human Context Protocol -- v2 $(DRAFT).docx" "$(HEADER)"
