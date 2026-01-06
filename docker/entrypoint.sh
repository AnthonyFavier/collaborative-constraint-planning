#!/bin/bash

# 1. Activate the venv
source env_cai/bin/activate

# 2. Execute the passed command
# "exec" replaces the shell process with your python process,
# ensuring signals (like Ctrl+C or SIGTERM) work correctly.
exec "$@"