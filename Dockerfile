# Use the official Python image as the base image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy requirements.txt (if it exists) and the project files
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

# Expose the port your app runs on (optional)
EXPOSE 8000

# Define the command to run your application
CMD ["python", "SuperNinja.py"]