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

# Create a shallow source release tarball and binary image tarball
#
# Run as:
# ./anms_release.sh
#
set -e

GITTAG=$(git describe --always --tags --dirty)

if [[ $# -ne 0 ]]
then
    echo "Usage: anms_release.sh"
    exit 1
fi

# Tarball of all source excluding git metadata
OUTFILE="anms-${GITTAG}-src.tar.gz"
DSTDIR=$(mktemp -d)
echo "Tarring source from ${DSTDIR} into ${OUTFILE}"
RSYNC_OPTS="--recursive --quiet --archive --delete --exclude=.git --exclude=puppet/.modules --exclude='*.tar.gz'"
rsync ${RSYNC_OPTS} ./ ${DSTDIR}/
tar -C ${DSTDIR} -czf ${OUTFILE} .
rm -rf ${DSTDIR}

# Tarball of all images
./build.sh tar
