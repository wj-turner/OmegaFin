#!/bin/bash

# Function to log messages
log() {
    echo "$(date +"%Y-%m-%d %T") - $1"
}

# Maximum number of attempts for the Alembic upgrade
max_attempts=5

# Delay in seconds between attempts
delay=10

# Start logging
log "Starting entrypoint script."

# Attempt Alembic Upgrade multiple times
for attempt in $(seq 1 $max_attempts); do
    log "Running Alembic upgrade, attempt $attempt of $max_attempts."
    output=$(alembic upgrade head 2>&1)
    exit_code=$?

    if [ $exit_code -eq 0 ]; then
        log "Alembic upgrade completed successfully."
        break
    else
        log "Alembic upgrade failed. Error Output: $output"
        if [ $attempt -eq $max_attempts ]; then
            log "Maximum attempts reached, failing."
            exit 1
        fi
        log "Retrying in $delay seconds..."
        sleep $delay
    fi
done

# Execute the passed command
log "Executing command: $@"
exec "$@"
