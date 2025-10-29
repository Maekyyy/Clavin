# Use the official Python image as a base
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the bot's code into the container
# Ensure your main bot file is named 'bot.py'
COPY . .

# Specify the command to run when the container starts
# This command executes your bot script
CMD ["python", "bot.py"]