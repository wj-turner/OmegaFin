#!/bin/bash

# Initialize Airflow (if not already done)
airflow db init

# Create a default user (skip if the user already exists)
airflow users list | grep 'admin' > /dev/null
if [ $? -ne 0 ]; then
    echo "Creating user..."
    airflow users create \
        --username test \
        --firstname John \
        --lastname Doe \
        --role Admin \
        --email admin@test.com \
        --password test
else
    echo "User already created"
fi

# Start Airflow webserver (or other command)
exec "$@"
