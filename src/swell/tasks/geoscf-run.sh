#!/bin/bash

# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------
# Submit gcm_run_geoscf.j via sbatch, capture its output to a known log file, and print it
# so the log is visible in the swell task output.
#
# Required environment variable:
#   SCRATCH_DIR  path to the scratch directory containing gcm_run_geoscf.j
# --------------------------------------------------------------------------------------------------

set -e

echo "SCRATCH_DIR = ${SCRATCH_DIR}"

GCM_SCRIPT=${SCRATCH_DIR}/gcm_run_geoscf.j
LOG_FILE=${SCRATCH_DIR}/gcm_run.log

echo "Submitting GCM job: ${GCM_SCRIPT}"

set +e
sbatch --wait --output=${LOG_FILE} ${GCM_SCRIPT}
EXIT_CODE=$?
set -e

echo "--- GCM run log ---"
cat ${LOG_FILE}

if [ ${EXIT_CODE} -ne 0 ]; then
    echo "Forecast job failed with exit code ${EXIT_CODE}"
    exit ${EXIT_CODE}
fi
