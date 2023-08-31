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

# Apply copyright and license markings to source files.
#
# Requires installation of:
#  pip3 install licenseheaders
# Run as:
#  ./apply_license.sh {--dry} {-vv}
#
set -e

SELFDIR=$(realpath $(dirname "${BASH_SOURCE[0]}"))

LICENSEOPTS="${LICENSEOPTS} --tmpl ${SELFDIR}/license.tmpl"
LICENSEOPTS="${LICENSEOPTS} --current-year"
# Excludes only apply to directory (--dir) mode and not file mode
LICENSEOPTS="${LICENSEOPTS} --exclude *.yml *.yaml *.min.* "


# Specific paths
if [ -n "$@" ]
then
    echo "Applying markings to selected $@ ..."
    licenseheaders ${LICENSEOPTS} --dir $@
    exit 0
fi



# Ensure each sub-repo contains a license file
for DIRNAME in amp-sql anms-core anms-core/ace anms-core/CAmpPython anms-ui aricodec transcoder
do

    if ! diff -q ${SELFDIR}/LICENSE ${SELFDIR}/${DIRNAME}/LICENSE
    then
        echo "Copying LICENSE to ${DIRNAME}"
        cp ${SELFDIR}/LICENSE ${SELFDIR}/${DIRNAME}/LICENSE
    fi
done

# Remove non-managed files
for DIRNAME in ion/src anms-ui/public/node_modules anms-ui/server/node_modules puppet/.modules
do
    rm -rf ${SELFDIR}/${DIRNAME}
done

echo "Applying markings to source..."
licenseheaders ${LICENSEOPTS} --dir ${SELFDIR}
for NAMEGLOB in '.gitlab-ci.yml' '*-compose.yml'
do
    for FILEPATH in $(find "${SELFDIR}" -type f -a -name "${NAMEGLOB}")
    do
        licenseheaders ${LICENSEOPTS} --file ${FILEPATH}
    done
done

# Restore non-managed files
(cd ${SELFDIR}/amp-sql && git restore mysql/Agent_Scripts/adm_*.sql)
(cd ${SELFDIR}/anms-core && git restore anms/static/assets/fastapi test/resources/public)
(cd ${SELFDIR} && git submodule update --init --recursive ion/src)
