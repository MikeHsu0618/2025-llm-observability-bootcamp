# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install google-adk
# We install directly here, but you could use a requirements.txt if needed
RUN pip install --no-cache-dir google-adk
RUN pip install --no-cache-dir openlit

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Define environment variable
ENV NAME World

# Run the ADK Web UI when the container launches
# We use --host 0.0.0.0 to make it accessible outside the container.
CMD ["adk", "web", "--port", "8000"] 