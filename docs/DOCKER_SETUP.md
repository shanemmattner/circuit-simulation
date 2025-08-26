# Docker Setup for Circuit Simulation

This guide explains how to use Docker to run circuit simulations with ngspice and PySpice, avoiding system conflicts with KiCad or other installed versions.

## Why Docker?

Using Docker provides several benefits:
- **Isolation**: No conflicts with system-installed ngspice/KiCad
- **Consistency**: Same environment across different systems
- **Portability**: Works on Linux, macOS, and Windows
- **Easy Setup**: Single command to get a working environment

## Quick Start

### 1. Build the Docker Image

```bash
# Using the helper script
./docker/run_simulation.sh build

# Or using docker-compose directly
docker-compose build circuit-sim
```

### 2. Run Simulations

```bash
# Run the simulation demo
./docker/run_simulation.sh demo

# Run any Python script
./docker/run_simulation.sh run examples/quick_start.py

# Start interactive Python shell
./docker/run_simulation.sh python

# Start bash shell in container
./docker/run_simulation.sh shell
```

### 3. Run Tests

```bash
./docker/run_simulation.sh test
```

## Docker Images

We provide two Dockerfile options:

### Ubuntu-based (Dockerfile)
- **Base**: Ubuntu 22.04
- **Size**: ~1.5GB
- **Features**: Full ngspice, Jupyter support, complete development environment
- **Use when**: You need full features, GUI support, or debugging tools

### Alpine-based (Dockerfile.alpine)
- **Base**: Alpine Linux
- **Size**: ~500MB
- **Features**: Minimal ngspice, basic Python environment
- **Use when**: You want minimal size, running in CI/CD, or production

To use Alpine version:
```bash
docker build -f Dockerfile.alpine -t circuit-sim:alpine .
```

## Docker Compose Services

The `docker-compose.yml` defines three services:

### circuit-sim (Main Service)
- Interactive development environment
- Full access to project files
- X11 forwarding for matplotlib plots

### notebook (Jupyter Service)
- Jupyter notebook server
- Access at http://localhost:8888
- No authentication token (development only!)

### test (Test Runner)
- Automated test execution
- Coverage reports
- CI/CD friendly

## Usage Examples

### Interactive Development

```bash
# Start a shell in the container
docker-compose run --rm circuit-sim bash

# Inside container, run Python interactively
python3
>>> from circuit_sim import Circuit
>>> c = Circuit("Test")
>>> c.add_resistor("R1", 1, 0, "1k")
```

### Running Scripts

```bash
# Run a specific example
docker-compose run --rm circuit-sim python3 examples/simulation_demo.py

# Run with custom environment variables
docker-compose run --rm -e PYSPICE_NGSPICE_LIBRARY=/custom/path circuit-sim python3 my_script.py
```

### Jupyter Notebooks

```bash
# Start Jupyter server
docker-compose up notebook

# Access in browser
open http://localhost:8888

# Stop when done
docker-compose down notebook
```

### Debugging

```bash
# Run with verbose output
docker-compose run --rm circuit-sim python3 -v examples/simulation_demo.py

# Check ngspice installation
docker-compose run --rm circuit-sim ngspice -v

# Check PySpice configuration
docker-compose run --rm circuit-sim python3 -c "import PySpice; print(PySpice.__version__)"
```

## Troubleshooting

### Issue: Docker build fails
**Solution**: Make sure Docker daemon is running and you have sufficient disk space.

### Issue: Cannot connect to Docker daemon
**Solution**: 
- Linux: Add user to docker group: `sudo usermod -aG docker $USER`
- macOS/Windows: Ensure Docker Desktop is running

### Issue: Matplotlib plots don't show
**Solution**: X11 forwarding is needed. On Linux:
```bash
xhost +local:docker
docker-compose run --rm circuit-sim python3 script_with_plots.py
```

### Issue: Permission denied errors
**Solution**: The Docker container runs as non-root user. Ensure files are readable:
```bash
chmod -R 755 .
```

### Issue: Ngspice not found
**Solution**: The ngspice library path might be different. Override it:
```bash
docker-compose run --rm \
  -e PYSPICE_NGSPICE_LIBRARY=/usr/lib/libngspice.so \
  circuit-sim python3 examples/simulation_demo.py
```

## Advanced Usage

### Custom Ngspice Build

To build ngspice from source with specific options:

```dockerfile
# Add to Dockerfile
RUN wget https://sourceforge.net/projects/ngspice/files/ngspice-38.tar.gz && \
    tar -xzf ngspice-38.tar.gz && \
    cd ngspice-38 && \
    ./configure --with-ngshared --enable-xspice --enable-cider && \
    make && \
    make install
```

### Mounting Additional Volumes

```yaml
# In docker-compose.yml
volumes:
  - ./data:/data  # Mount data directory
  - ~/.config:/home/simulator/.config  # Share config
```

### Running in Production

For production deployments:

1. Use Alpine image for smaller size
2. Remove Jupyter and development tools
3. Run as read-only filesystem:
```bash
docker run --read-only --tmpfs /tmp circuit-sim:alpine
```

## CI/CD Integration

### GitHub Actions

```yaml
name: Test
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Build Docker image
        run: docker build -t circuit-sim .
      - name: Run tests
        run: docker run --rm circuit-sim pytest
```

### GitLab CI

```yaml
test:
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker build -t circuit-sim .
    - docker run --rm circuit-sim pytest
```

## Performance Tips

1. **Use BuildKit**: `DOCKER_BUILDKIT=1 docker build .`
2. **Layer caching**: Order Dockerfile commands from least to most frequently changed
3. **Multi-stage builds**: Separate build and runtime dependencies
4. **Volume mounts**: Use for development, copy for production

## Security Considerations

1. Don't run containers as root in production
2. Use specific version tags, not `latest`
3. Scan images for vulnerabilities: `docker scan circuit-sim`
4. Limit resources: `docker run --memory=1g --cpus=2`
5. Use secrets management for sensitive data

## Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Ngspice Documentation](http://ngspice.sourceforge.net/docs.html)
- [PySpice Documentation](https://pyspice.fabrice-salvaire.fr/)

---

For issues or questions, please open an issue on the project repository.