# Build stage
FROM python:3.9-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create and activate virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Tesseract and other system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-eng \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Runtime stage
FROM python:3.9-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-eng \
    libgl1-mesa-glx \
    libglib2.0-0 \
    espeak \
    portaudio19-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy Python virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DISPLAY=:0 \
    QT_X11_NO_MITSHM=1 \
    XDG_RUNTIME_DIR=/tmp/xdg

# Create a non-root user
RUN useradd -m -u 1000 maya
USER maya
WORKDIR /home/maya/app

# Copy application code
COPY --chown=maya:maya . .

# Set up runtime directories
RUN mkdir -p /home/maya/.config/maya /home/maya/.local/share/maya
VOLUME ["/home/maya/.config/maya", "/home/maya/.local/share/maya"]

# Set default command
CMD ["python", "main.py"]
