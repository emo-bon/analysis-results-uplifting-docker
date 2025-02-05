# Note: Ensure variable declarations in makefiles have NO trailing whitespace
#       This can be achieved by sliding in the # comment-sign directly after the value
PROJECT := "arup"#              - this code is for uplifting of the analysis results in the emobon project
BUILD_TAG ?= latest#            - provide the BUILD_TAG in the environment, or fallback to latest
REG_NS ?= "emobon"#             - allow the namespace to be overridden to e.g. ghcr.io/emo-bon/emobon

N_TAG := ${REG_NS}_${PROJECT}#  - the versionless "name" docker image tag
V_TAG := ${REG_NS}_${PROJECT}:${BUILD_TAG}# - the full docker image tag
FLAKE8_EXCLUDE := .venv,venv,.git,.tox,dist,build,*.egg-info# - the directories to exclude from flake8 checks

.PHONY: help docker-build docker-push docker-test init check lint-fix test clean
.DEFAULT_GOAL := help


help:  ## Shows this list of available targets and their effect.
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'


# usage `make BUILD_TAG=0.2 docker-build` to include a specific tag to the build docker images
docker-build: ## Builds the docker-image
	@echo "building the arup image with  tag: -t ${V_TAG}"
	@env docker build -t ${V_TAG} --no-cache .
	

# usage `make REG_NS=ghcr.io/emob-bon/emobon docker-build` to push images to github-container-registry
docker-push: docker-build ## Builds, then pushes the docker-images to ${REG_NS}
	@echo "pushing docker images tagged=${V_TAG}"
ifeq ($(shell echo ${REG_NS} | egrep '.+/.+'),)  # the 'shell' call is essential
# empty match indicates no registry-part is available to push to
	@echo "not pushing docker images if no / between non-empty parts in REG_NS=${REG_NS}"
	@exit 1
else
	docker push ${V_TAG};
endif


docker-test: ## Launches local-named variants of the containers/images in docker-compose.yml
	@echo "launching docker for local test on rocrate in ./tests/data"
	@docker run --rm --name emo-bon_${PROJECT} --volume ./tests/data:/rocrateroot ${N_TAG}
	@echo "todo -- check up the outcome in some way or another"

.venv/touchfile: requirements.txt requirements-dev.txt
	@echo "initializing the python environment for the project"
	@test -d .venv || python3 -m venv .venv
	@. .venv/bin/activate; pip install -Ur requirements.txt; pip install -Ur requirements-dev.txt
	@touch .venv/touchfile

# usage `touch requirements.txt; make init` to force a re-init if e.g. external dependencies (like sema) have new versions
init: .venv/touchfile ## Initializes the python environment for the project

check: ## Checks the code for linting and formatting issues
	@echo "checking the code for linting and formatting issues"
	@flake8 .  --exclude ${FLAKE8_EXCLUDE} --ignore=E203,W503

lint-fix: ## Fixes the code for linting and formatting issues
	@echo "fixing the code for linting and formatting issues"
	@black .
	@isort .

test: ## Runs the tests for the project
	@echo "running the tests for the project"
	@pytest tests/

clean: ## Cleans the python environment for the project
	@echo "cleaning the python environment for the project"
	@rm -rf .venv
	@find . -iname "*.pyc" -delete
