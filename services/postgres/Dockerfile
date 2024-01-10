# Base image
FROM timescale/timescaledb:latest-pg12

# Set the environment variables
ENV POSTGRES_DB=mydatabase
ENV POSTGRES_USER=myuser
ENV POSTGRES_PASSWORD=mypassword

# Expose the default Postgres port
EXPOSE 5432

# Set the entrypoint command
CMD ["postgres"]


# Use the official PostgreSQL image as the base image
FROM postgres:latest

# Install the TimescaleDB extension
RUN apt-get update && apt-get install -y timescaledb-2-postgresql-13

# Copy the TimescaleDB configuration file to the correct location
COPY timescaledb.conf /etc/postgresql/postgresql.conf.d/timescaledb.conf

# Expose port 5432 to allow external connections
EXPOSE 5432

# Set the default environment variables for Postgres
ENV POSTGRES_USER postgres
ENV POSTGRES_PASSWORD password
ENV POSTGRES_DB database

# Start the PostgreSQL server
CMD [ "postgres", "-c", "config_file=/etc/postgresql/postgresql.conf" ]
