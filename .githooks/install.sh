#!/usr/bin/env bash

ln -s ${PWD}/.githooks/update-env-hook.sh ${PWD}/.git/hooks/post-commit
ln -s ${PWD}/.githooks/update-env-hook.sh ${PWD}/.git/hooks/post-checkout
ln -s ${PWD}/.githooks/update-env-hook.sh ${PWD}/.git/hooks/post-merge
ln -s ${PWD}/.githooks/update-env-hook.sh ${PWD}/.git/hooks/post-rewrite
