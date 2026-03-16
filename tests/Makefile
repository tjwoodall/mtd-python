MAKEFLAGS += -rR

.SECONDEXPANSION:

OTHER := everything hello api

# everything: test everything
# hello: run hello-world tests
# api: run api tests

ALL := $(patsubst tests/%.json,%,$(filter-out $(OTHER),$(wildcard tests/*.json)))
HELLO_TARGETS := $(patsubst tests/%.json,%,$(filter-out $(OTHER),$(wildcard tests/hello-*.json)))

all:
	@$(foreach t,$(OTHER),printf "%-45s %s\n" "$(t)" "$$(sed -n 's/^# $(t): //p' $(MAKEFILE_LIST))";)
	@echo
	@$(foreach t,$(sort $(HELLO_TARGETS)),printf "%-45s %s\n" "$(t)" "$$(sed -n 's/^ *"description": *//p' tests/$(t).json)";)
	@echo
	@$(foreach t,$(filter-out $(HELLO_TARGETS),$(sort $(ALL))),printf "%-45s %s\n" "$(t)" "$$(sed -n 's/^ *"description": *//p' tests/$(t).json)";)

clean:
	rm -f artifacts/sandbox-tests/*
	rm -f tests/examples/*
	tools/make-tests.py artifacts/webscrape.json
	tools/make-tests.py artifacts/application.json

.PHONY: $(OTHER) $(ALL)

everything: $(ALL)
	@:

api: $(filter-out $(HELLO_TARGETS),$(ALL))
	@:

hello: $(HELLO_TARGETS)
	@:

$(ALL): %: artifacts/sandbox-tests/%
	@:

artifacts/sandbox-tests/%: tests/%.json $$(wildcard tests/$$(word 1,$$(subst ., ,$$*))/*)
	mkdir -p artifacts/cache/
	mkdir -p $(@D)
	tools/test-outbound-edits.py tests/$*.json >$@.tmp 2>&1
	mv $@.tmp $@

