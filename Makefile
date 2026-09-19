# DataCivicLab — Sistema Bancario
TOOLKIT = toolkit
PREFIX = sistema_bancario
export TOOLKIT_ALLOW_SCRIPT_SOURCE = 1

DATASETS := $(shell find datasets -name dataset.yml 2>/dev/null | sort)
COMPOSE  := $(shell find compose -name dataset.yml 2>/dev/null | sort)

.PHONY: seeds
seeds:
	@for f in $(DATASETS); do \
		echo "=== $$f ==="; \
		$(TOOLKIT) run --config "$$f" || exit 1; \
	done

.PHONY: run-compose
run-compose:
	@for f in $(COMPOSE); do \
		echo "=== $$f ==="; \
		$(TOOLKIT) run --config "$$f" || exit 1; \
	done

.PHONY: run-all
run-all: seeds run-compose

.PHONY: check
check:
	@for f in $(DATASETS) $(COMPOSE); do \
		echo "-> $$f"; \
		$(TOOLKIT) run preflight --config "$$f" > /dev/null 2>&1 || exit 1; \
	done
	@echo "✅ All configs valid"

.PHONY: clean
clean:
	rm -rf out/data/_runs out/data/probe out/data/raw out/data/clean out/data/mart out/data/cross .tmp/

.PHONY: clean-runs
clean-runs:
	rm -rf out/data/_runs/

.PHONY: registry registry-write
registry:
	$(TOOLKIT) registry build --prefix $(PREFIX)

registry-write:
	$(TOOLKIT) registry build --prefix $(PREFIX) --write

.PHONY: test
test:
	pytest tests/ -v

.PHONY: dashboard
dashboard:
	streamlit run dashboard/app.py

.PHONY: dashboard-test
dashboard-test:
	python3 -m pytest dashboard/tests/ -v

.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:' Makefile | sort
