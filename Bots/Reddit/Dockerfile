FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create non-root user
RUN useradd -ms /bin/bash appuser
USER appuser

# Default command: stream with env-configured subs/keywords
CMD ["python", "-m", "bot.main", "stream"]