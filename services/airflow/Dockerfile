# Use the official Airflow image as a parent image
FROM apache/airflow:2.8.1

WORKDIR /opt/airflow
RUN pip install psycopg2-binary

# Copy the entrypoint script
COPY entrypoint.sh entrypoint.sh

# Set the entrypoint
ENTRYPOINT ["/opt/airflow/entrypoint.sh"]
# CMD ["tail", "-f", "/dev/null"]
