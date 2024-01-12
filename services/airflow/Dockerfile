# Base image
FROM apache/airflow:2.2.0

# Set the environment variables
ENV AIRFLOW__CORE__SQL_ALCHEMY_CONN=postgresql+psycopg2://myuser:mypassword@postgres:5432/mydatabase
ENV AIRFLOW__CORE__EXECUTOR=CeleryExecutor

# Expose the default Airflow ports
EXPOSE 8080 8793

# Set the entrypoint command
ENTRYPOINT ["./entrypoint.sh"]