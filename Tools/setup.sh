#!/usr/bin/env bash
# Prepare the sibling Delta rive checkout; accepts --delta PATH.
RIVE_WORKFLOW_MODE=setup
source "$(dirname "${BASH_SOURCE[0]}")/delta-workflow.sh"
