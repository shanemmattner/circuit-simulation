#!/bin/bash
# Script to run circuit simulations in Docker container

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_warning "docker-compose not found, using 'docker compose' instead"
    COMPOSE_CMD="docker compose"
else
    COMPOSE_CMD="docker-compose"
fi

# Parse command line arguments
COMMAND=${1:-shell}
shift || true

case $COMMAND in
    build)
        print_info "Building Docker image..."
        $COMPOSE_CMD build circuit-sim
        print_info "Docker image built successfully!"
        ;;
    
    shell)
        print_info "Starting interactive shell in container..."
        $COMPOSE_CMD run --rm circuit-sim bash
        ;;
    
    python)
        print_info "Starting Python interpreter in container..."
        $COMPOSE_CMD run --rm circuit-sim python3
        ;;
    
    run)
        if [ -z "$1" ]; then
            print_error "Please specify a Python file to run"
            exit 1
        fi
        print_info "Running $1 in container..."
        $COMPOSE_CMD run --rm circuit-sim python3 "$@"
        ;;
    
    test)
        print_info "Running tests in container..."
        $COMPOSE_CMD run --rm test
        ;;
    
    demo)
        print_info "Running simulation demo..."
        $COMPOSE_CMD run --rm circuit-sim python3 examples/simulation_demo.py
        ;;
    
    notebook)
        print_info "Starting Jupyter notebook server..."
        print_info "Access notebook at: http://localhost:8888"
        $COMPOSE_CMD up notebook
        ;;
    
    clean)
        print_info "Cleaning up Docker containers and images..."
        $COMPOSE_CMD down
        docker rmi circuit-simulation:latest || true
        print_info "Cleanup complete!"
        ;;
    
    help)
        echo "Circuit Simulation Docker Helper"
        echo ""
        echo "Usage: $0 [COMMAND] [OPTIONS]"
        echo ""
        echo "Commands:"
        echo "  build       Build the Docker image"
        echo "  shell       Start an interactive bash shell"
        echo "  python      Start an interactive Python shell"
        echo "  run FILE    Run a Python file"
        echo "  test        Run the test suite"
        echo "  demo        Run the simulation demo"
        echo "  notebook    Start Jupyter notebook server"
        echo "  clean       Remove containers and images"
        echo "  help        Show this help message"
        echo ""
        echo "Examples:"
        echo "  $0 build"
        echo "  $0 run examples/quick_start.py"
        echo "  $0 demo"
        echo "  $0 test"
        ;;
    
    *)
        print_error "Unknown command: $COMMAND"
        echo "Run '$0 help' for usage information"
        exit 1
        ;;
esac