# This must be the first this in Makefile
# https://stackoverflow.com/a/324782
# Variables expanded here...
BASE_DIR := $(dir $(CURDIR)/$(word $(words $(MAKEFILE_LIST)),$(MAKEFILE_LIST)))
ROOT_DIR := $(patsubst %/,%,$(BASE_DIR))
THIS_FILE := $(ROOT_DIR)/Makefile
THIS_DIR := $(notdir $(patsubst %/,%,$(ROOT_DIR)))

WEB_DIR := $(ROOT_DIR)
WEB_UI_DIR := $(ROOT_DIR)/public
WEB_UI_RELEASE_DIR := $(ROOT_DIR)/release
WEB_SERVER_DIR := $(ROOT_DIR)/server

# Variables expanded upon reference...
YARN_GBIN_DIR = $(shell yarn global bin)
WHOAMI = $(shell whoami)

# https://stackoverflow.com/a/2527627 (old way...)
NPROCS := 1
OS := $(shell uname -s)
ifeq ($(OS),Linux)
  NPROCS := $(shell nproc)
endif
ifeq ($(OS),Darwin) # Assume Mac OS X
  NPROCS := $(shell nproc)
endif

## Top-level Functions

.PHONY: up down build debug clean test docker-up docker-down docker-build docker-logs

up: build
	@echo "Starting Necessary Services"
	cd $(WEB_DIR) && $(YARN_GBIN_DIR)/pm2 start process.yml

down:
	@echo "Stopping Necessary Services"
	cd $(WEB_DIR) && $(YARN_GBIN_DIR)/pm2 delete process.yml

build: build-server build-ui setup-db
	@echo "Finished..."

debug:
	@echo System: $(OS)
	@echo $(BASE_DIR)
	@echo $(ROOT_DIR)
	@echo $(THIS_FILE)
	@echo $(THIS_DIR)
	@echo Processes: $(NPROCS)
	@echo MakeFlags: $(MAKEFLAGS)

clean: clean-server clean-ui clean-ui-release
	@echo "Finished..."

test:
	@echo "Nothing to test yet..."

docker-up: docker-build
	docker-compose up -d

docker-down:
	docker-compose down

docker-build: export DOCKER_BUILDKIT = 1
docker-build: export COMPOSE_DOCKER_CLI_BUILD = 1
docker-build:
	docker-compose build

docker-logs:
	docker-compose logs -f


## Build Functions

.PHONY: build-server build-ui

build-server: setup-server-daemon setup-server
	$(YARN_GBIN_DIR)/pm2 describe pm2-logrotate > /dev/null || $(YARN_GBIN_DIR)/pm2 -s install pm2-logrotate
	$(YARN_GBIN_DIR)/pm2 -s set pm2-logrotate:retain 30
	$(YARN_GBIN_DIR)/pm2 -s set pm2-logrotate:compress false
	$(YARN_GBIN_DIR)/pm2 -s set pm2-logrotate:max_size 100M
	$(YARN_GBIN_DIR)/pm2 -s set pm2-logrotate:dateFormat YYYY-MM-DD_HH-mm-ss
	$(YARN_GBIN_DIR)/pm2 -s set pm2-logrotate:rotateInterval "0 0 * * *"

build-ui: setup-ui
	cd $(WEB_UI_DIR) && yarn build

## Setup Functions

.PHONY: setup-server-daemon setup-server setup-ui setup-db

setup-server-daemon:
	yarn global add pm2 rimraf
	$(YARN_GBIN_DIR)/pm2 update

setup-server:
	cd $(WEB_SERVER_DIR) && yarn install

setup-ui:
	cd $(WEB_UI_DIR) && yarn install

## Clean Functions

.PHONY: clean-server clean-ui clean-ui-release clean-venv

clean-server:
	-$(YARN_GBIN_DIR)/pm2 uninstall pm2-logrotate
	-cd $(WEB_SERVER_DIR) && $(YARN_GBIN_DIR)/rimraf node_modules

clean-ui:
	-cd $(WEB_UI_DIR) && $(YARN_GBIN_DIR)/rimraf node_modules

clean-ui-release:
	-cd $(WEB_DIR) && $(YARN_GBIN_DIR)/rimraf "release/**/!(.gitignore)"

## Misc Functions

.PHONY: ramdisk-osx ramdisk-osx-clean

ramdisk-osx:
	if $$(diskutil info $(WEB_UI_RELEASE_DIR) > /dev/null); then exit 1; else exit 0; fi
	ram_device=$$(hdiutil attach -nomount ram://$$((2 * 1024 * 300))) \
	&& newfs_hfs -s -v chronolens_ramdisk $$ram_device \
	&& mount -t hfs $$ram_device $(WEB_UI_RELEASE_DIR)
	cd $(WEB_UI_RELEASE_DIR) && touch .gitignore && printf "*\n!.gitignore\n" > .gitignore

ramdisk-osx-clean:
	if $$(diskutil info $(WEB_UI_RELEASE_DIR) > /dev/null); then exit 0; else exit 1; fi
	diskutil eject chronolens_ramdisk
