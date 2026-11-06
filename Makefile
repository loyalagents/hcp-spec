DRAFT ?= 2.0-draft-3
SPEC = $(if $(wildcard spec/$(DRAFT)/source),spec/$(DRAFT)/source,spec/$(DRAFT))
FILES = $(if $(wildcard spec/$(DRAFT)/source),$(shell python3 -I -c 'import sys; sys.path.insert(0, "tools"); import restructure; print(" ".join(restructure.FILES))'),title_clean.md $(foreach n,$(shell seq 1 27),s$(n).md))
SCHEMAS = schemas/$(DRAFT)
HEADER ?= Human Context Protocol (HCP) v2  |  Draft Specification  |  November 2026

.PHONY: schemas check docx pages

schemas:
	python3 -I tools/make_schemas.py $(SCHEMAS) $(DRAFT)

check: schemas
	python3 -I tools/check_schemas.py $(SCHEMAS) $(SPEC)

docx:
	mkdir -p out
	for f in $(FILES); do cat $(SPEC)/$$f; printf '\n'; done > out/$(DRAFT).md
	python3 -I tools/build.py template/template.docx out/$(DRAFT).md "out/Human Context Protocol -- v2 $(DRAFT).docx" "$(HEADER)"

pages:
	python3 -I tools/make_pages.py $(SPEC) spec/$(DRAFT) $(DRAFT)
