#!make
ROOT_PY3 := python3

POETRY := $(shell which poetry)
POETRY_VARS :=
ifeq ($(shell uname -s),Darwin)
	HOMEBREW_OPENSSL_DIR := $(shell brew --prefix openssl)
	POETRY_VARS += CFLAGS="-I$(HOMEBREW_OPENSSL_DIR)/include"
	POETRY_VARS += LDFLAGS="-L$(HOMEBREW_OPENSSL_DIR)/lib"
endif

BLACK := $(POETRY) run black
ISORT := $(POETRY) run isort
PYLINT := $(POETRY) run pylint
PYTEST := $(POETRY) run pytest
PYTHON := $(POETRY) run python3

TAG_LATEST := false
DOCKER_IMAGE ?= godaddy-dynamic-dns
DOCKER_IMAGE_TAG ?= latest
DOCKER_IMAGE_TAG_DEV ?= dev
DOCKER_SOURCE_IMAGE_TAG ?= $(DOCKER_IMAGE_TAG)
DOCKER := docker
IMAGE_REPOSITORY := alanquillin
REPOSITORY_IMAGE ?= $(DOCKER_IMAGE)

ifeq ("$(wildcard .env)","")
$(shell touch .env)
endif

include .env
export $(shell sed 's/=.*//' .env)

ifeq ($(TAG_LATEST),true)
override DOCKER_BUILD_ARGS += -t $(IMAGE_REPOSITORY)/$(REPOSITORY_IMAGE):latest
endif


.PHONY: build build-dev clean depends format lint publish run-dev

# dependency targets

depends: 
	$(POETRY_VARS) $(POETRY) install --no-root

update-depends:
	$(POETRY_VARS) $(POETRY) update

# Targets for building containers

# prod
build: depends
ifeq ($(VERSION),)
	$(error VERSION was not provided)
endif
	$(DOCKER) buildx build --platform=linux/amd64,linux/arm64,linux/arm $(DOCKER_BUILD_ARGS) -t $(IMAGE_REPOSITORY)/$(REPOSITORY_IMAGE):$(VERSION) .

# dev

build-dev: depends
	$(DOCKER) build $(DOCKER_BUILD_ARGS) -t $(DOCKER_IMAGE):$(DOCKER_IMAGE_TAG_DEV) .

# Targets for publishing containers

publish:
	$(MAKE) build DOCKER_BUILD_ARGS+="--push"

# Targets for running the app

run-dev: build-dev
	$(DOCKER) run --env-file .env $(DOCKER_IMAGE):$(DOCKER_IMAGE_TAG_DEV)

# Testing and Syntax targets

lint: depends
	$(ISORT) --check-only godaddy_dynamic_dns
	$(PYLINT) godaddy_dynamic_dns
	$(BLACK) --check godaddy_dynamic_dns

format: depends
	$(ISORT) godaddy_dynamic_dns
	$(BLACK) godaddy_dynamic_dns

# Clean up targets

clean:
	docker rmi $(DOCKER_IMAGE):$(DOCKER_IMAGE_TAG)
