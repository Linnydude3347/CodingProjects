FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Default command: poll mentions with env-configured settings
CMD ["python", "-m", "x_bot.main", "reply-mentions"]