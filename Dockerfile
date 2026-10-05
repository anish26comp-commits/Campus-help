# ============================================================
# Campus Help Server Docker Image
# ============================================================

FROM python:3.13-slim

# Working directory
WORKDIR /app

# Copy dependencies
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY server ./server
COPY database ./database
COPY files ./files

# TCP application server
EXPOSE 5000

# UDP discovery
EXPOSE 5001/udp

# FTP control connection
EXPOSE 2121

# FTP passive data ports
EXPOSE 30000-30009

# HTTP server
EXPOSE 8000

# Start application
CMD ["python", "-u", "server/server.py"]