# Circuit Simulation Docker Container
# Based on Ubuntu with ngspice and PySpice for electronic circuit simulation

FROM ubuntu:22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYSPICE_NGSPICE_LIBRARY=/usr/lib/x86_64-linux-gnu/libngspice.so.0

# Install system dependencies
RUN apt-get update && apt-get install -y \
    # Python and pip
    python3.11 \
    python3.11-dev \
    python3-pip \
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
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user
RUN useradd -m -s /bin/bash simulator && \
    mkdir -p /workspace && \
    chown -R simulator:simulator /workspace

# Set working directory
WORKDIR /workspace

# Install Python packages
RUN pip3 install --no-cache-dir \
    numpy \
    scipy \
    matplotlib \
    PySpice \
    plotly \
    pandas \
    jupyter \
    ipython \
    pytest \
    pytest-cov \
    black \
    ruff \
    mypy

# Copy the project files
COPY --chown=simulator:simulator . /workspace/

# Install the circuit-sim package in development mode
RUN pip3 install -e .

# Switch to non-root user
USER simulator

# Expose port for Jupyter (optional)
EXPOSE 8888

# Default command
CMD ["/bin/bash"]