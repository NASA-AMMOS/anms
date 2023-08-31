#!/bin/bash
##
## Copyright (c) 2023 The Johns Hopkins University Applied Physics
## Laboratory LLC.
##
## This file is part of the Asynchronous Network Management System (ANMS).
##
## Licensed under the Apache License, Version 2.0 (the "License");
## you may not use this file except in compliance with the License.
## You may obtain a copy of the License at
##     http://www.apache.org/licenses/LICENSE-2.0
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.
##
## This work was performed for the Jet Propulsion Laboratory, California
## Institute of Technology, sponsored by the United States Government under
## the prime contract 80NM0018D0004 between the Caltech and NASA under
## subcontract 1658085.
##

# Create a shallow release copy for ANMS on the AMMOS Github.
#
# Run as:
# ./anms_release.sh master v0.9.0 v0.9.0
#
set -e

SRCBRANCH=$1
SRCTAG=$2
DSTTAG=$3
if ! shift 3
then
    echo "Usage: anms_release.sh {SRC_BRANCH} {SRC_TAG} {DST_TAG} [--dry-run]"
    exit 1
fi
DOPUSH=1
if [ "$1" == "--dry-run" ]
then
    DOPUSH=0
    echo "Running in dry-run mode, no changes will be pushed to the remote"
fi

SRCREPO="git@gitlab.jhuapl.edu:anms/ammos-anms.git"
DSTREPO="git@github.jpl.nasa.gov:MGSS/anms.git"

TMPDIR=$(mktemp -d)
echo "Working in ${TMPDIR} ..."
pushd ${TMPDIR} >/dev/null

read -p "Push enter when APL VPN is active..."
while ! git clone ${SRCREPO} --depth 1 --branch ${SRCBRANCH} --single-branch --recurse-submodules src
do
    echo "Some failure occurred above."
    read -p "Push enter to try again..."
done

# Tag locally
if [ -n "${SRCTAG}" ]
then
    # Separate versioning for ACE and CAmp
    for DIRNAME in . amp-sql anms-core anms-ui transcoder
    do
	echo "Tagging ${SRCTAG} in ${DIRNAME}"
	pushd src/${DIRNAME} >/dev/null
	git tag -a ${SRCTAG} -m "Release ${SRCTAG}" --force
	if [ $DOPUSH -ne 0 ]
	then
	    git push --tags --force
	fi
	popd
    done
fi


# No need for these files
for FN in .git .gitmodules .gitlab-ci.yml
do
    find src -name "${FN}" -exec rm -rf {} +
done

read -p "Push enter when JPL VPN is active..."
while ! git clone ${DSTREPO} dst
do
    echo "Some failure occurred above."
    read -p "Push enter to try again..."
done

RSYNC_OPTS="--recursive --quiet --archive --delete --exclude .git"
rsync ${RSYNC_OPTS} src/ dst/
# Add to the destination
pushd dst >/dev/null
git add -A
git status
git commit -m "Updating for release ${DSTTAG}" || true
git tag -a ${DSTTAG} -m "Release ${DSTTAG}"
if [ $DOPUSH -ne 0 ]
then
    while ! git push
    do
        echo "Some failure occurred above."
        read -p "Push enter to try again..."
    done
    git push --tags
fi
popd

echo "Finished in ${TMPDIR}"
popd
