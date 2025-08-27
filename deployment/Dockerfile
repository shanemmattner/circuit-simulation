# Circuit Simulation Docker Container
# Multi-architecture support for both x86_64 and ARM64 (Apple Silicon)

FROM python:3.11-slim

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Build tools
    build-essential \
    cmake \
    git \
    wget \
    curl \
    # Libraries for ngspice
    libxaw7-dev \
    libreadline-dev \
    libncurses5-dev \
    libxml2-dev \
    libfftw3-dev \
    libblas-dev \
    liblapack-dev \
    # Ngspice
    ngspice \
    libngspice0-dev \
    # Additional tools
    vim \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Find and set the ngspice library path dynamically
RUN export NGSPICE_LIB=$(find /usr/lib -name "libngspice.so*" | head -1) && \
    echo "export PYSPICE_NGSPICE_LIBRARY=${NGSPICE_LIB}" >> /etc/profile && \
    echo "Found ngspice library at: ${NGSPICE_LIB}"

# Create a non-root user
RUN useradd -m -s /bin/bash simulator && \
    mkdir -p /workspace && \
    chown -R simulator:simulator /workspace

# Set working directory
WORKDIR /workspace

# Copy requirements files first (for better caching)
COPY requirements.txt requirements-dev.txt ./

# Install uv (modern Python package manager)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Install Python packages
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r requirements-dev.txt && \
    pip install --no-cache-dir \
        ipywidgets>=8.1.1 \
        jupyter>=1.0.0 \
        jupyterlab>=4.0.0 \
        voila>=0.5.0 \
        jupyter-dash>=0.4.2 \
        ipython>=8.12.0 \
        nbformat>=5.9.0 \
        nbconvert>=7.0.0

# Copy the project files
COPY --chown=simulator:simulator . /workspace/

# Install the circuit-sim package in development mode
RUN pip install -e .

# Switch to non-root user
USER simulator

# Source the profile to get environment variables
SHELL ["/bin/bash", "-c"]

# Expose ports
EXPOSE 8888 8000

# Default command - source profile and start bash
CMD ["/bin/bash", "-l"]