# Use an official Python runtime as a parent image
FROM python:3.11.2

# Set the working directory in the container
WORKDIR /api

# Copy the current directory contents into the container
COPY . /api

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable (optional)
# ENV VARIABLE_NAME variable_value

# Run your application
CMD ["python", "runserver.py"]
