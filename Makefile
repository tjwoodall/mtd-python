.ONESHELL:
.SUFFIXES:
.DELETE_ON_ERROR:
MAKEFLAGS += -rR

SHELL := /bin/bash
.SHELLFLAGS := -e -x -o pipefail -c

#ifndef VIRTUAL_ENV
#$(error You must activate a Python virtual environment before running make)
#endif

# Patterns here are <api>/<version>
UNSUPPORTED :=

#### IMPORTANT ####
#
# This makefile rebases and force pushes. Ensure you understand the scope and
# impact of any changes before testing. It also does work in a worktree that is
# subsequently pruned meaning that git reflog will not help.
#
# Because of this, the fixes to the APIs necessary to generate the json can be
# irretrivably lost. There are tags created that should preserve older commits
#
# Tags created:
# webscrape_ts_<timestamp>           - fixed up tree as of committer <timestamp> of the last commit of the webscrape.clean fixups
# main_<timestamp>                   - fixed up tree as of committer <timestamp> of the last commit of the hmrc/main fixups
# fixup-externalValue-tag            - Tag points to commit that is hmrc/main with externalValues fixed up.
# fixup-externalValue-webscrape-tag  - Tag points to commit that is webscrape.clean with externalValues fixed up.
#
# YOU HAVE BEEN WARNED.
#

# This needs .netrc setup
# root@dirac:/# cat ~/.netrc
# machine github.com
# login $(OWNER)
# password github_pat_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# remember to update ~/.netrc when the github token changes
PREFIX := /api-documentation/docs/api/service
DOMAIN := https://developer.service.hmrc.gov.uk$(PREFIX)
GITHUB_TOKEN := $(shell cat .github.token)
OWNER := tjwoodall

OneDayAgo := $(shell echo $$(( $$( date +%s ) - 86400 )) )

# DependsOn: curl ca-certificates python3 python3-typeguard python3-lxml libcpp-hocon-dev libleatherman-dev libjsoncpp-dev python3-ruamel.yaml python3-openapi-spec-validator jq npm python3-rfc3987 python3-jsonschema python3-requests python3-netifaces
# Recomments: python3-mypy python3-typeshed
#
# npm i @redocly/cli
#
###############################################
# No longer required
# apt-get install pip python3.13-venv
# python3 -m venv --system-site-packages .venv
# source .venv/bin/activate
# pip install jsonschema
# pip install rfc3987
###############################################

# Makefile depends on this so this is downloaded (once per day) when make is run
ALLAPIHTML = artifacts/api.html

# extract all the APIS from the html
APIS := $(sort $(foreach p,$(shell [[ -f $(ALLAPIHTML) ]] && tools/get-api-links.py $(ALLAPIHTML)),$(word 5,$(subst /, ,$(p)))))

.PHONY: force

.PHONY: all
all: everything

Makefile :: $(ALLAPIHTML)
	touch Makefile

$(ALLAPIHTML): $(shell [[ -f $(ALLAPIHTML) && $$( stat -c %Y "$(ALLAPIHTML)" 2>/dev/null || echo 0 ) -gt $(OneDayAgo) ]] || echo force )
	mkdir -p artifacts/docs
	curl --fail -s -o $(ALLAPIHTML) "https://developer.service.hmrc.gov.uk/api-documentation/docs/api"

tools/hocon-to-json: tools/hocon-to-json.cpp
	g++ -o tools/hocon-to-json tools/hocon-to-json.cpp -ljsoncpp -lcpp-hocon

validate-example-deps := $(shell tools/pydeps.py tools/validate-example.py )
find-bad-formats-deps := $(shell tools/pydeps.py tools/find-bad-formats.py )
test-inbound-renderer-deps := $(shell tools/pydeps.py tools/test-inbound-renderer.py )
test-outbound-renderer-deps := $(shell tools/pydeps.py tools/test-outbound-renderer.py )
yaml-to-json-deps := $(shell tools/pydeps.py tools/yaml-to-json.py )
update-endpoint-status-deps := $(shell tools/pydeps.py tools/update-endpoint-status.py )
merge-common-errors-deps := $(shell tools/pydeps.py tools/merge-common-errors.py )

define WITH_WEBSCRAPE_WORKTREE
	trap '[[ -z $$$${WEBSCRAPETMP} ]] || rm -fr $$$${WEBSCRAPETMP}/; git -C $(1) worktree prune' EXIT
	WEBSCRAPETMP=$$$$( mktemp -d -p. )
	git -C $(1) worktree add $(2) ../$$$${WEBSCRAPETMP} $(3)
endef

define TAG_WEBSCRAPE
	if git merge-base --is-ancestor webscrape.clean webscrape; then
	  tag="webscrape_ts_$$$$( git show -s --format=%ct webscrape )"
	  if [[ "$$$$( git rev-parse --quiet "$$$$tag^{}" 2>/dev/null )" != $$$$( git rev-parse webscrape ) ]]; then
	    msg=$$$$( git log -1 webscrape.clean --format="Patched HMRC %cd (%H) on $$$$(date)" )
	    git tag -f -a -m "$$$$msg" "$$$$tag" webscrape
	  fi
	fi
endef

define TAG_MAIN
	if git merge-base --is-ancestor hmrc/main main; then
	  tag="main_$$$$( git show -s --format=%ct main )"
	  if [[ "$$$$( git rev-parse --quiet "$$$$tag^{}" 2>/dev/null )" != $$$$( git rev-parse main ) ]]; then
	    msg=$$$$( git log -1 hmrc/main --format="Patched HMRC %cd (%H) on $$$$(date)" )
	    git tag -f -a -m "$$$$msg" "$$$$tag" main
	  fi
	fi
endef

artifacts/docs/redoc.standalone.js:
	curl -o $@ https://cdn.redocly.com/redoc/v2.5.1/bundles/redoc.standalone.js

artifacts/docs/logo-mini.svg:
	curl -o $@ https://cdn.redoc.ly/redoc/logo-mini.svg
	sed -i 's|https://cdn.redoc.ly/redoc/||' $@

define APIRULE

# Makefile depends on this so it is downloaded (once per day) when make is run
$(eval APIHTML := artifacts/$(1)-main.html)

$(APIHTML) $(APIHTML).change-stamp: $$(shell [[ -f "$(APIHTML)" && $$$$( stat -c %Y "$(APIHTML)" 2>/dev/null || echo 0 ) -gt $(OneDayAgo) ]] || echo force)
	curl --fail -L -s -o "$(APIHTML)" "$(DOMAIN)/$(1)"
	touch -d "$$$$(tools/get-changed-date.py $(APIHTML))" $(APIHTML).change-stamp

Makefile :: $(APIHTML) | $(1)
	touch Makefile

$(eval GITVERSIONS := $(subst $(1)/,, \
	$(filter-out $(UNSUPPORTED), \
		$(patsubst $(1)/resources/public/api/conf/%/application.yaml,$(1)/%,$(wildcard $(1)/resources/public/api/conf/*/application.yaml) ) \
	) \
) )
$(eval VERSIONS := $(subst $(1)/,, \
	$(filter-out $(UNSUPPORTED), \
		$(patsubst /api-documentation/docs/api/service/%/oas/page,%,$(shell [[ -f $(APIHTML) ]] && tools/get-endpoint-links.py "$(APIHTML)" ) ) \
	) \
) )

# This tag file gets updated every time main gets a new head commit (hash)
artifacts/$(1).tag: force | $(1)
	cd "$(1)"
	git rev-parse main >../$$@.tmp
	diff -q ../$$@ ../$$@.tmp || mv ../$$@.tmp ../$$@
	rm -f ../$$@.tmp

# Setup $(1) if it doesn't exist. If it exists at hmrc, we clone it to $$(OWNER) and then clone that to here.
# if it doesn't exist at hmrc then we create an empty repo at $$(OWNER)
# create the webscrape and webscrape.clean branches if they don't exit.
# Makefile depends on this so it gets fetched/created when make is run
$(1):
	@echo
	@echo "Processing $(1)"
	clone() {
	  # If the api exists as a git repo at hmrc then fork it otherwise create an api at github.
	  status=$$$$( curl -s -o /dev/null -u "$(OWNER):$(GITHUB_TOKEN)" -w "%{http_code}" "https://api.github.com/repos/hmrc/$(1)" )
	  [[ $$$${status} -eq 200 ]] || { sleep 2; status=$$$$( curl -s -o /dev/null -u "$(OWNER):$(GITHUB_TOKEN)" -w "%{http_code}" "https://api.github.com/repos/hmrc/$(1)" ); }
	  [[ $$$${status} -eq 200 ]] || { sleep 2; status=$$$$( curl -s -o /dev/null -u "$(OWNER):$(GITHUB_TOKEN)" -w "%{http_code}" "https://api.github.com/repos/hmrc/$(1)" ); }
	  if [[ $$$${status} -eq 200 ]]; then
	    curl -s -u "$(OWNER):$(GITHUB_TOKEN)" -X POST "https://api.github.com/repos/hmrc/$(1)/forks"
	  else
	    curl -H "Authorization: token $(GITHUB_TOKEN)" -H "Accept: application/vnd.github+json" https://api.github.com/user/repos -d '{"name":"$(1)","private":false}'
	  fi
	  sleep 10
	  status=$$$$( curl -s -o /dev/null -u "$(OWNER):$(GITHUB_TOKEN)" -w "%{http_code}" "https://api.github.com/repos/$(OWNER)/$(1)" )
	  [[ $$$${status} -eq 200 ]] || { sleep 10; status=$$$$( curl -s -o /dev/null -u "$(OWNER):$(GITHUB_TOKEN)" -w "%{http_code}" "https://api.github.com/repos/$(OWNER)/$(1)" ); }
	  [[ $$$${status} -eq 200 ]] || { sleep 10; status=$$$$( curl -s -o /dev/null -u "$(OWNER):$(GITHUB_TOKEN)" -w "%{http_code}" "https://api.github.com/repos/$(OWNER)/$(1)" ); }
	  [[ $$$${status} -eq 200 ]]
	}
	trap 'rm -fr $(1)' EXIT
	status=$$$$( curl -s -o /dev/null -u "$(OWNER):$(GITHUB_TOKEN)" -w "%{http_code}" "https://api.github.com/repos/$(OWNER)/$(1)" )
	[[ $$$${status} -eq 200 ]] || { sleep 2; status=$$$$( curl -s -o /dev/null -u "$(OWNER):$(GITHUB_TOKEN)" -w "%{http_code}" "https://api.github.com/repos/$(OWNER)/$(1)" ); }
	[[ $$$${status} -eq 200 ]] || { sleep 2; status=$$$$( curl -s -o /dev/null -u "$(OWNER):$(GITHUB_TOKEN)" -w "%{http_code}" "https://api.github.com/repos/$(OWNER)/$(1)" ); }
	[[ $$$${status} -eq 200 ]] || clone
	# at this point we know that the repo
	if git config -f .gitmodules --get-regex submodule.$(1); then
	  git submodule update --init $(1)
	else
	  git clone "https://github.com/$(OWNER)/$(1).git" "$(1)"
	  (
	    cd "$(1)"
	    if ! git rev-parse --verify --quiet webscrape.clean; then
	      if git rev-parse --verify --quiet origin/webscrape.clean; then
	        git branch -f webscrape.clean origin/webscrape.clean
	      else
	        git checkout --orphan webscrape.clean
	        git reset --hard
	        git commit --allow-empty -m "empty commit"
	      fi
	    fi
	    if ! git rev-parse --verify --quiet webscrape; then
	      if git rev-parse --verify --quiet origin/webscrape; then
	        git branch -f webscrape origin/webscrape
	      else
	        git branch -f webscrape webscrape.clean
	      fi
	    fi
	    git checkout main
	    status=$$$$( curl -s -o /dev/null -u "$(OWNER):$(GITHUB_TOKEN)" -w "%{http_code}" "https://api.github.com/repos/hmrc/$(1)" )
	    [[ $$$${status} -eq 200 ]] || { sleep 2; status=$$$$( curl -s -o /dev/null -u "$(OWNER):$(GITHUB_TOKEN)" -w "%{http_code}" "https://api.github.com/repos/hmrc/$(1)" ); }
	    [[ $$$${status} -eq 200 ]] || { sleep 2; status=$$$$( curl -s -o /dev/null -u "$(OWNER):$(GITHUB_TOKEN)" -w "%{http_code}" "https://api.github.com/repos/hmrc/$(1)" ); }
	    if [[ $$$${status} -eq 200 ]]; then
	      git remote add hmrc "https://github.com/hmrc/$(1).git"
	    elif ! git rev-parse --verify --quiet hmrc/main; then
	      if git rev-parse --verify --quiet origin/hmrc/main; then
	        git branch -f hmrc/main origin/hmrc/main
	      else
	        git branch -f hmrc/main webscrape.clean
	      fi
	    fi
	  )
	  git submodule add -f "https://github.com/$(OWNER)/$(1).git" "$(1)"
	fi
	trap - EXIT

# This pushes everything up to github
.PHONY: $(1).push
$(1).push:
	cd "$(1)"
	git merge-base --is-ancestor hmrc/main main
	git merge-base --is-ancestor webscrape.clean webscrape
	git merge-base --is-ancestor fixup-externalValue-webscrape-tag webscrape
	! git remote get-url hmrc &>/dev/null || git merge-base --is-ancestor fixup-externalValue-tag main
	$(TAG_WEBSCRAPE)
	$(TAG_MAIN)
	git push --force --tags || git push --force --tags
	if ! git remote get-url hmrc &>/dev/null; then
	  [[ $$$$(git rev-parse origin/hmrc/main 2>/dev/null) == $$$$(git rev-parse hmrc/main) ]] || git push --force-with-lease origin hmrc/main || git push --force-with-lease origin hmrc/main
	fi
	[[ $$$$(git rev-parse origin/main 2>/dev/null) == $$$$(git rev-parse main) ]] || git push --force-with-lease origin main || git push --force-with-lease origin main
	[[ $$$$(git rev-parse origin/webscrape 2>/dev/null) == $$$$(git rev-parse webscrape) ]] || git push --force-with-lease origin webscrape || git push --force-with-lease origin webscrape
	[[ $$$$(git rev-parse origin/webscrape.clean 2>/dev/null) == $$$$(git rev-parse webscrape.clean) ]] || git push origin webscrape.clean || git push origin webscrape.clean

# This is the entry point for updating the $$(OWNER) repo with the data from HMRC
.PHONY: $(1).pull
$(1).pull: $(1).fetch $(1).webscrape $(1).webscrape-resolved $(1).webscrape-redocly | $(1)

.PHONY: $(1).rebase
$(1).rebase: $(1).rebase-main $(1).rebase-webscrape | $(1)

# This rebases the main branch onto hmrc/main
.PHONY: $(1).rebase-main
$(1).rebase-main: $(if $(filter $(2),$(VERSIONS)),$(1).rebase-webscrape) | $(1)
	cd "$(1)"
	git remote get-url hmrc &>/dev/null || git branch -f hmrc/main webscrape.clean
	if ! git merge-base --is-ancestor hmrc/main main; then
	  [[ "$$$$(git symbolic-ref --short HEAD)" = "main" ]]
	  git diff --quiet
	  git diff --cached --quiet
	  trap 'git reset --hard HEAD; git clean -fd; git switch main' EXIT
	  git switch --detach hmrc/main
	  if [[ "$(1)" == "trader-goods-profiles" ]]; then
	    # Nobody every heard of consistency? Why does this API do it in a completely different way? It's specific to this single file, doesn't support versionning, and doesn't support, for example, examples in separate files that need templating.
	    # It's a trivial conversion to convert it to something equivalent to EVERY other api! (which we do here)
	    ../tools/schemaTemplateToHB.py app/uk/gov/hmrc/tradergoodsprofiles/templates/ApiSchema.scala.txt >resources/public/api/conf/1.0/application.yaml
	    git add resources/public/api/conf/1.0/application.yaml
	    git commit -m "Put back application.yaml - generated by ../tools/schemaTemplateToHB.py app/uk/gov/hmrc/tradergoodsprofiles/templates/ApiSchema.scala.txt >resources/public/api/conf/1.0/application.yaml"
	    ../tools/fixup-externalValue-local.sh
	    git commit -a -m "Fixup externalValue and normalise Restricted" || true
	    if [[ "$$$$(git rev-parse HEAD^{tree})" != "$$$$(git rev-parse fixup-externalValue-tag^{tree} 2>/dev/null || true)" ||
	          "$$$$(git rev-parse HEAD^^)" != "$$$$(git rev-parse fixup-externalValue-tag^^ 2>/dev/null || true)" ]]; then
	      git tag -f fixup-externalValue-tag HEAD
	    fi
	  else
	    ../tools/fixup-externalValue-local.sh
	    git add resources
	    git commit -a -m "Fixup externalValue and normalise Restricted" || true
	    if [[ "$$$$(git rev-parse HEAD^{tree})" != "$$$$(git rev-parse fixup-externalValue-tag^{tree} 2>/dev/null || true)" ||
	          "$$$$(git rev-parse HEAD^)" != "$$$$(git rev-parse fixup-externalValue-tag^ 2>/dev/null || true)" ]]; then
	      git tag -f fixup-externalValue-tag HEAD
	    fi
	  fi
	  git switch main
	  trap - EXIT
	  git rebase --exec ../tools/fixup-eol.py -Xignore-space-at-eol fixup-externalValue-tag
	fi
	git merge-base --is-ancestor hmrc/main main
	$(TAG_MAIN)

.PHONY: $(1).fetch
$(1).fetch: | $(1)
ifeq ($(intcmp 0$(shell [[ -f artifacts/$(1).fetch.tag ]] && stat -c %Y artifacts/$(1).fetch.tag 2>/dev/null),$(OneDayAgo),lt,eq,gt),lt)
	(
	  cd "$(1)"
	  if ! git remote get-url hmrc &>/dev/null; then
	    status=$$$$( curl -s -o /dev/null -u "$(OWNER):$(GITHUB_TOKEN)" -w "%{http_code}" "https://api.github.com/repos/hmrc/$(1)" )
	    [[ $$$${status} -ne 200 ]]
	    # TODO - need the magic to link to the now appeared github repo...
	  fi
	  $(TAG_MAIN)
	  git fetch --all -p || git fetch --all -p
	)
	date "+%s" > artifacts/$(1).fetch.tag
else
	echo "$$@ up to date"
endif

# This rebases the webscrape branch onto the webscrape.clean branch.
.PHONY: $(1).rebase-webscrape
$(1).rebase-webscrape: | $(1)
	if ! git -C "$(1)" merge-base --is-ancestor webscrape.clean webscrape; then
$(call WITH_WEBSCRAPE_WORKTREE,$(1),,webscrape)
	  (
	    cd $$$${WEBSCRAPETMP}
	    git switch --detach webscrape.clean
	    ../tools/fixup-externalValue-local.sh
	    git commit -a -m "Fixup externalValue and normalise Restricted" || true
	    if [[ "$$$$(git rev-parse HEAD^{tree})" != "$$$$(git rev-parse fixup-externalValue-webscrape-tag^{tree} 2>/dev/null || true)" ||
	          "$$$$(git rev-parse HEAD^)" != "$$$$(git rev-parse fixup-externalValue-webscrape-tag^ 2>/dev/null || true)" ]]; then
	      git tag -f fixup-externalValue-webscrape-tag HEAD
	    fi
	    git switch webscrape
	    git rebase --exec ../tools/fixup-eol.py -Xignore-space-at-eol fixup-externalValue-webscrape-tag
	    git merge-base --is-ancestor webscrape.clean webscrape
	    $(TAG_WEBSCRAPE)
	  )
	fi

.PHONY: $(1).cleanup
$(1).cleanup:
$(call WITH_WEBSCRAPE_WORKTREE,$(1),,webscrape.clean)
	cd $$$${WEBSCRAPETMP}
	for d in resources/public/api/conf/*; do
	  v=$${d##*/}
	  case " $(VERSIONS) " in
	    *" $$v "*) ;;
	    *) echo rm -rf "$$d" ;;
	  esac
	done

# This fetches the underlying files used to drive the website documentation and commits them to the webscrape.clean branch
.PHONY: $(1).webscrape
$(1).webscrape: $(foreach v,$(VERSIONS),artifacts/$(1).$(v).webscrape.downloaded)
	$(foreach v,$(filter-out $(VERSIONS), $(notdir $(wildcard $(1)/resources/public/api/conf/*))),echo rm -fr $(1)/resources/public/api/conf/$v)

# This fetches the oas/resolved spec from hmrc and commits it to the webscrape.clean branch
.PHONY: $(1).webscrape-resolved
$(1).webscrape-resolved: $(foreach v,$(VERSIONS),artifacts/$(1).$(v).webscrape-resolved.downloaded)

# This does a redocly bundle of the underlying files used to drive the website documentation and commits them to the webscrape.clean branch
.PHONY: $(1).webscrape-redocly
$(1).webscrape-redocly: $(foreach v,$(VERSIONS),artifacts/$(1).$(v).webscrape-redocly.downloaded)

# convert the hocon application.conf into a json config.
artifacts/$(1).config.json: tools/hocon-to-json artifacts/$(1).tag $(1)/conf/application.conf $(update-endpoint-status-deps)
	echo
	echo "Processing $1"
	tools/hocon-to-json "$$@.tmp" $(1)/conf/application.conf
	tools/update-endpoint-status.py "$$@.tmp" $(APIHTML)
	mv "$$@.tmp" "$$@"

artifacts/$(1).json: $(foreach v,$(GITVERSIONS),artifacts/$(1).$(v).json)
	tools/merge-json.py $$@ $$^

.PHONY: artifacts/docs/$(1).html
artifacts/docs/$(1).html: $(foreach v,$(GITVERSIONS),artifacts/docs/$(1).$(v).html)

artifacts/$(1).json.validate: $(foreach v,$(GITVERSIONS),artifacts/$(1).$(v).json.validate)
	touch $$@

artifacts/$(1).json.examples: $(foreach v,$(GITVERSIONS),artifacts/$(1).$(v).json.examples)
	touch $$@

artifacts/$(1).json.badformats: $(foreach v,$(GITVERSIONS),artifacts/$(1).$(v).json.badformats)
	touch $$@

artifacts/$(1).json.outbound: $(foreach v,$(GITVERSIONS),artifacts/$(1).$(v).json.outbound)
	touch $$@

artifacts/$(1).json.inbound: $(foreach v,$(GITVERSIONS),artifacts/$(1).$(v).json.inbound)
	touch $$@


artifacts/$(1).webscrape.json: $(foreach v,$(VERSIONS),artifacts/$(1).$(v).webscrape.json)
	tools/merge-json.py $$@ $$^

.PHONY: artifacts/docs/$(1).webscrape.html
artifacts/docs/$(1).webscrape.html: $(foreach v,$(VERSIONS),artifacts/docs/$(1).$(v).webscrape.html)

artifacts/$(1).webscrape.json.validate: $(foreach v,$(VERSIONS),artifacts/$(1).$(v).webscrape.json.validate)
	touch $$@

artifacts/$(1).webscrape.json.examples: $(foreach v,$(VERSIONS),artifacts/$(1).$(v).webscrape.json.examples)
	touch $$@

artifacts/$(1).webscrape.json.badformats: $(foreach v,$(VERSIONS),artifacts/$(1).$(v).webscrape.json.badformats)
	touch $$@

artifacts/$(1).webscrape.json.outbound: $(foreach v,$(VERSIONS),artifacts/$(1).$(v).webscrape.json.outbound)
	touch $$@

artifacts/$(1).webscrape.json.inbound: $(foreach v,$(VERSIONS),artifacts/$(1).$(v).webscrape.json.inbound)
	touch $$@

artifacts/$(1).redocly.json: $(foreach v,$(VERSIONS),artifacts/$(1).$(v).redocly.json)
	tools/merge-json.py $$@ $$^

$(foreach v,$(sort $(VERSIONS) $(GITVERSIONS)),$(call JSONRULE,$(1),$(v)))

endef

define RENDERRULE

artifacts/$(1).$(2).json.$(3).$(4): artifacts/$(1).$(2).json.hash $(test-$(3)-renderer-deps)
	tools/test-$(3)-renderer.py artifacts/$(1).$(2).json --partition $(4)/4 >/dev/null
	touch $$@

endef

define WEBSCRAPERENDERRULE

artifacts/$(1).$(2).webscrape.json.$(3).$(4): artifacts/$(1).$(2).webscrape.json.hash $(test-$(3)-renderer-deps) $(if $(filter $(2),$(GITVERSIONS)),artifacts/$(1).$(2).json.hash)
	if ! cmp -s artifacts/$(1).$(2).json.hash artifacts/$(1).$(2).webscrape.json.hash; then
	  tools/test-$(3)-renderer.py artifacts/$(1).$(2).webscrape.json --partition $(4)/4 >/dev/null
	fi
	touch $$@

endef

define JSONRULE


# This fetches the underlying files used to drive the website documentation and commits them to the webscrape.clean branch
artifacts/$(1).$(2).webscrape.downloaded: $(APIHTML).change-stamp | $(1)
$(call WITH_WEBSCRAPE_WORKTREE,$(1),,webscrape.clean)
	(
	  cd $$$${WEBSCRAPETMP}
	  $(TAG_WEBSCRAPE)
	  ../tools/webscrape.sh $1 $2 resources/public/api/conf
	  git add .
	  git commit -a -m "Scraped underlying docs for $(2) at $$$$(date)" || true
	)
	touch $$@

# This fetches the oas/resolved spec from hmrc and commits it to the webscrape.clean branch
artifacts/$(1).$(2).webscrape-resolved.downloaded: $(APIHTML).change-stamp | $(1)
$(call WITH_WEBSCRAPE_WORKTREE,$(1),,webscrape.clean)
	(
	  cd $$$${WEBSCRAPETMP}
	  $(TAG_WEBSCRAPE)
	  curl --fail -s -o "resolved.$2.yaml" "$(DOMAIN)/$1/$2/oas/resolved"
	  git add .
	  git commit -a -m "Scraped resolved for $(2) at $$$$(date)" || true
	)
	touch $$@

# This does a redocly bundle of the underlying files used to drive the website documentation and commits them to the webscrape.clean branch
artifacts/$(1).$(2).webscrape-redocly.downloaded: $(APIHTML).change-stamp | $(1)
$(call WITH_WEBSCRAPE_WORKTREE,$(1),,webscrape.clean)
	(
	  cd $$$${WEBSCRAPETMP}
	  $(TAG_WEBSCRAPE)
	  NODE_OPTIONS="--require ../tools/undici-proxy.js" npx redocly bundle --dereferenced --remove-unused-components --output redocly.resolved.$2.yaml $(DOMAIN)/$1/$2/oas/application.yaml
	  git add .
	  git commit -a -m "Scraped and bundled for $(2) at $$$$(date)" || true
	)
	touch $$@

.NOTPARALLEL: artifacts/$(1).$(2).webscrape.downloaded artifacts/$(1).$(2).webscrape-resolved.downloaded artifacts/$(1).$(2).webscrape-redocly.downloaded
# Generate a timestamp file for the tree at resources/public/api/conf/<version>
artifacts/$(1).$(2).tag: force | $(1)
	cd "$(1)"
	git rev-parse main:$$$$(realpath --relative-to . resources/public/api/conf/$(2)) >../$$@.tmp
	diff -q ../$$@ ../$$@.tmp || mv ../$$@.tmp ../$$@
	rm -f ../$$@.tmp

artifacts/$(1).$(2).webscrape.tag: force | $(1)
	cd "$(1)"
	git rev-parse webscrape:resources/public/api/conf/$(2) >../$$@.tmp
	diff -q ../$$@ ../$$@.tmp || mv ../$$@.tmp ../$$@
	rm -f ../$$@.tmp

# Generate the json api using yaml-to-json
artifacts/$(1).$(2).json.hash: artifacts/$(1).$(2).json
	cat artifacts/$(1).$(2).json | sha256sum >$$@.tmp
	cmp -s $$@ $$@.tmp || mv $$@.tmp $$@
	rm -f $$@.tmp

artifacts/$(1).$(2).json artifacts/$(1).$(2).extraconfig.json &: artifacts/$(1).tag artifacts/$(1).config.json $(yaml-to-json-deps) $(merge-common-errors-deps)
	( cd $(1) && [ "$$$$(git symbolic-ref --short HEAD)" = "main" ] )
	tools/yaml-to-json.py --include-deprecated $(1) artifacts/$(1).$(2).json artifacts/$(1).config.json artifacts/$(1).$(2).extraconfig.json $(1)/resources/public/api/conf/$2/application.yaml
	tools/merge-common-errors.py artifacts/$(1).$(2).json

artifacts/$(1).$(2).webscrape.json.hash: artifacts/$(1).$(2).webscrape.json
	cat artifacts/$(1).$(2).webscrape.json | sha256sum >$$@.tmp
	cmp -s $$@ $$@.tmp || mv $$@.tmp $$@
	rm -f $$@.tmp

artifacts/$(1).$(2).webscrape.json artifacts/$(1).$(2).webscrape.extraconfig.json &: artifacts/$(1).$(2).webscrape.tag artifacts/$(1).config.json $(yaml-to-json-deps) $(merge-common-errors-deps)
$(call WITH_WEBSCRAPE_WORKTREE,$(1),--detach,webscrape)
	tools/yaml-to-json.py --include-deprecated $(1) artifacts/$(1).$(2).webscrape.json artifacts/$(1).config.json artifacts/$(1).$(2).webscrape.extraconfig.json $$$${WEBSCRAPETMP}/resources/public/api/conf/$2/application.yaml
	tools/merge-common-errors.py artifacts/$(1).$(2).webscrape.json

# Document the schema using redocly
artifacts/docs/$(1).$(2).html: artifacts/$(1).$(2).json.hash artifacts/docs/logo-mini.svg artifacts/docs/redoc.standalone.js
	trap 'rm -f $$@.json $$@.tmp' EXIT
	jq 'to_entries[] | .value | to_entries[] | .value | to_entries[] | .value' "artifacts/$(1).$(2).json" >$$@.json
	npx redocly build-docs $$@.json -o $$@.tmp --disableGoogleFont
	sed -i 's|https://cdn.redocly.com/redoc/v2.5.1/bundles/||' $$@.tmp
	mv $$@.tmp $$@

artifacts/docs/$(1).$(2).webscrape.html: artifacts/$(1).$(2).webscrape.json.hash $(if $(filter $(2),$(GITVERSIONS)),artifacts/docs/$(1).$(2).html) artifacts/docs/redoc.standalone.js artifacts/docs/logo-mini.svg
	trap 'rm -f $$@.json $$@.tmp' EXIT
	if ! cmp -s artifacts/$(1).$(2).json.hash artifacts/$(1).$(2).webscrape.json.hash; then
	  jq 'to_entries[] | .value | to_entries[] | .value | to_entries[] | .value' "artifacts/$(1).$(2).webscrape.json" >$$@.json
	  npx redocly build-docs $$@.json -o $$@.tmp --disableGoogleFont
	  sed -i 's|https://cdn.redocly.com/redoc/v2.5.1/bundles/||' $$@.tmp
	  mv $$@.tmp $$@
	else
	  cp artifacts/docs/$(1).$(2).html $$@
	fi

# Validate the schema using redocly
artifacts/$(1).$(2).json.validate: artifacts/$(1).$(2).json.hash
	trap 'rm -f $$@.json $$@.tmp' EXIT
	jq 'to_entries[] | .value | to_entries[] | .value | to_entries[] | .value' "artifacts/$(1).$(2).json" >$$@.json
	npx redocly lint $$@.json --format=json |& tee $$@.tmp
	mv $$@.tmp $$@

artifacts/$(1).$(2).webscrape.json.validate: artifacts/$(1).$(2).webscrape.json.hash $(if $(filter $(2),$(GITVERSIONS)),artifacts/$(1).$(2).json.validate)
	trap 'rm -f $$@.json $$@.tmp' EXIT
	if ! cmp -s artifacts/$(1).$(2).json.hash artifacts/$(1).$(2).webscrape.json.hash; then
	  jq 'to_entries[] | .value | to_entries[] | .value | to_entries[] | .value' "artifacts/$(1).$(2).webscrape.json" >$$@.json
	  npx redocly lint $$@.json --format=json |& tee $$@.tmp
	  mv $$@.tmp $$@
	else
	  cp artifacts/$(1).$(2).json.validate $$@
	fi

# Validate that the examples comply with the schema
artifacts/$(1).$(2).json.examples: artifacts/$(1).$(2).json.hash $(validate-example-deps)
	tools/validate-example.py artifacts/$(1).$(2).json
	touch $$@

artifacts/$(1).$(2).webscrape.json.examples: artifacts/$(1).$(2).webscrape.json.hash $(validate-example-deps) $(if $(filter $(2),$(GITVERSIONS)),artifacts/$(1).$(2).json.examples)
	if ! cmp -s artifacts/$(1).$(2).json.hash artifacts/$(1).$(2).webscrape.json.hash; then
	  tools/validate-example.py artifacts/$(1).$(2).webscrape.json
	fi
	touch $$@

# Check for bad formats
artifacts/$(1).$(2).json.badformats: artifacts/$(1).config.json artifacts/$(1).$(2).extraconfig.json $(find-bad-formats-deps) artifacts/$(1).$(2).tag
	tools/find-bad-formats.py $(1) artifacts/$(1).config.json artifacts/$(1).$(2).extraconfig.json $(1)/resources/public/api/conf/$2/application.yaml
	touch $$@

artifacts/$(1).$(2).webscrape.json.badformats: artifacts/$(1).config.json artifacts/$(1).$(2).webscrape.extraconfig.json $(find-bad-formats-deps) artifacts/$(1).$(2).webscrape.tag
$(call WITH_WEBSCRAPE_WORKTREE,$(1),--detach,webscrape)
	tools/find-bad-formats.py $(1) artifacts/$(1).config.json artifacts/$(1).webscrape.extraconfig.json $$$${WEBSCRAPETMP}/resources/public/api/conf/$2/application.yaml
	touch $$@

# Test outbound rendering in libreoffice
artifacts/$(1).$(2).json.outbound: $(foreach p,0 1 2 3,artifacts/$(1).$(2).json.outbound.$(p))
	touch $$@

$(foreach p,0 1 2 3,$(call RENDERRULE,$(1),$(2),outbound,$(p)))

artifacts/$(1).$(2).webscrape.json.outbound: $(foreach p,0 1 2 3,artifacts/$(1).$(2).webscrape.json.outbound.$(p))
	touch $$@

$(foreach p,0 1 2 3,$(call WEBSCRAPERENDERRULE,$(1),$(2),outbound,$(p)))

# Test inbound rendering in libreoffice
artifacts/$(1).$(2).json.inbound: $(foreach p,0 1 2 3,artifacts/$(1).$(2).json.inbound.$(p))
	touch $$@

$(foreach p,0 1 2 3,$(call RENDERRULE,$(1),$(2),inbound,$(p)))

artifacts/$(1).$(2).webscrape.json.inbound: $(foreach p,0 1 2 3,artifacts/$(1).$(2).webscrape.json.inbound.$(p))
	touch $$@

$(foreach p,0 1 2 3,$(call WEBSCRAPERENDERRULE,$(1),$(2),inbound,$(p)))



# Generate the webscrape version of the api using redocly
artifacts/$(1).$(2).redocly.json : artifacts/$(1).$(2).webscrape.tag $(merge-common-errors-deps)
$(call WITH_WEBSCRAPE_WORKTREE,$(1),--detach,webscrape)
	if [[ -f $$$${WEBSCRAPETMP}/resources/public/api/conf/$(2)/application.yaml ]]; then
	  npx redocly bundle $$$${WEBSCRAPETMP}/resources/public/api/conf/$(2)/application.yaml --dereferenced --remove-unused-components --ext json | \
	    jq 'walk(if type=="object" then del(.definitions) else . end)' |
	    jq -S 'del(.components.schemas) | del(.components.responses) | del(.components.parameters) | del(.components.examples) | { "$(1)": { "$(word 1,$(subst ., ,$(2)))": { "$(word 2,$(subst ., ,$(2)))": .}}}' >artifacts/$(1).$(2).redocly.json
	else
	  echo '{}' | jq -S '{ "$(1)": { "$(word 1,$(subst ., ,$(2)))": { "$(word 2,$(subst ., ,$(2)))": .}}}' >artifacts/$(1).$(2).redocly.json
	fi
	tools/merge-common-errors.py artifacts/$(1).$(2).redocly.json

endef

.PHONY: pull
pull: $(foreach p,$(APIS),$(p).pull)

.PHONY: rebase
rebase: $(foreach p,$(APIS),$(p).rebase)

.PHONY: push
push: $(foreach p,$(APIS),$(p).push)

.PHONY: json
json: artifacts/application.json artifacts/webscrape.json artifacts/redocly.json

.PHONY: webscrape-cleanup
webscrape-cleanup: $(foreach p,$(APIS),$(p).cleanup)

.PHONY: docs
docs: $(foreach p,$(APIS),artifacts/docs/$(p).html) $(foreach p,$(APIS),artifacts/docs/$(p).webscrape.html)

.PHONY: validate
validate: $(foreach p,$(APIS),artifacts/$(p).json.validate) $(foreach p,$(APIS),artifacts/$(p).webscrape.json.validate)

.PHONY: examples
examples: $(foreach p,$(APIS),artifacts/$(p).json.examples) $(foreach p,$(APIS),artifacts/$(p).webscrape.json.examples)

.PHONY: badformats
badformats: $(foreach p,$(APIS),artifacts/$(p).json.badformats) $(foreach p,$(APIS),artifacts/$(p).webscrape.json.badformats)

.PHONY: outbound
outbound: $(foreach p,$(APIS),artifacts/$(p).json.outbound) $(foreach p,$(APIS),artifacts/$(p).webscrape.json.outbound)

.PHONY: inbound
inbound: $(foreach p,$(APIS),artifacts/$(p).json.inbound) $(foreach p,$(APIS),artifacts/$(p).webscrape.json.inbound)

artifacts/application.json: $(foreach p,$(APIS),artifacts/$(p).json)
	tools/merge-json.py artifacts/application.json $^

artifacts/webscrape.json: $(foreach p,$(APIS),artifacts/$(p).webscrape.json)
	tools/merge-json.py artifacts/webscrape.json $^

artifacts/redocly.json: $(foreach p,$(APIS),artifacts/$(p).redocly.json)
	tools/merge-json.py artifacts/redocly.json $^

.PHONY: everything
everything: json validate examples badformats outbound inbound docs
	tools/save-artifacts.sh

# setup every api
$(eval $(foreach p,$(APIS),$(call APIRULE,$(p))))

# These targets talk to github or the hmrc developer website so should not run in parallel (nor their dependencies)
.NOTPARALLEL: $(foreach p,$(APIS),$(p) $(p).fetch $(p).pull $(p).push $(p).rebase-main $(p).rebase-webscrape $(p).webscrape $(p).webscrape-resolved $(p).webscrape-redocly) Makefile pull push

$(info $(call APIRULE,common-transit-convention-traders))
