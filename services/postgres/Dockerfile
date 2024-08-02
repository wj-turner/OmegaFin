# Use the TimescaleDB image as the base image
# FROM timescale/timescaledb:latest-pg12
FROM timescale/timescaledb:2.16.0-pg16
# Set the default environment variables for Postgres
# ENV POSTGRES_DB=mydatabase
# ENV POSTGRES_USER=myuser
# ENV POSTGRES_PASSWORD=mypassword

# Expose port 5432 to allow external connections
EXPOSE 5432

# Copy the TimescaleDB configuration file, if you have any
# COPY timescaledb.conf /etc/postgresql/postgresql.conf.d/

# Start the PostgreSQL server with TimescaleDB
CMD ["postgres"]
