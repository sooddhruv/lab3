# Use the official Python 3.9 image as the base image
FROM python:3.9

# Update package lists and clean up
RUN apt-get update \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Create a user and group for running the application
RUN groupadd -g 799 nyu && \
    useradd -r -u 999 -g nyu nyu

# Set the working directory to /app
WORKDIR /app

# Copy the application files into the container
COPY . /app

# Install required Python packages
RUN pip install Flask requests docker

# Switch to the 'nyu' user
USER nyu

# Specify the default command to run when the container starts
CMD [ "python", "./FS.py" ]
