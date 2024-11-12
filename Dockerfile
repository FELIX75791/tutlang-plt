# Use the latest official Python runtime as a parent image
FROM python:latest

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container
COPY . .

# Install any Python dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make the lexer script executable (optional but useful)
RUN chmod +x tut_lexer.sh
RUN chmod +x tut_parser.sh

# Start the container with an interactive shell for manual execution
CMD ["/bin/bash"]
