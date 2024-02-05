# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /usr/src/app/

# Copy the current directory contents into the container at /usr/src/app
COPY . .
COPY src/entrypoint.sh entrypoint.sh
# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt


ENTRYPOINT ["/usr/src/app/entrypoint.sh"]
# Command to run on container start (here, we're just keeping the container running)
# CMD ["python", "src/process_data.py"]
CMD ["tail", "-f", "/dev/null"]