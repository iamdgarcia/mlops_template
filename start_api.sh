#!/bin/bash

# Fraud Detection API Startup Script

echo "Starting Fraud Detection API..."

# Set script directory as working directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Function to check if API is running
check_api_health() {
    local max_attempts=30
    local attempt=1
    
    echo "Waiting for API to be healthy..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s -f http://localhost:8000/health > /dev/null 2>&1; then
            echo "SUCCESS API is healthy!"
            return 0
        fi
        
        echo "   Attempt $attempt/$max_attempts - API not ready yet..."
        sleep 2
        ((attempt++))
    done
    
    echo "ERROR API failed to become healthy after $max_attempts attempts"
    return 1
}

# Function to run with Docker
run_with_docker() {
    echo "🐳 Running with Docker..."
    
    # Build the Docker image
    echo "🔨 Building Docker image..."
    if command -v docker-compose >/dev/null 2>&1; then
        docker-compose build
        if [ $? -ne 0 ]; then
            echo "ERROR Docker build failed"
            exit 1
        fi

        # Start the service
        echo "Starting Docker container..."
        docker-compose up -d
        if [ $? -ne 0 ]; then
            echo "ERROR Docker startup failed"
            exit 1
        fi

        # Check health
        check_api_health

        if [ $? -eq 0 ]; then
            echo "🎉 API is running successfully!"
            echo "INFO Access the API at: http://localhost:8000"
            echo "📚 API documentation at: http://localhost:8000/docs"
            echo "🔍 To view logs: docker-compose logs -f"
            echo "🛑 To stop: docker-compose down"
        fi

    else
        # Fallback to using `docker compose` (modern Docker CLI)
        if docker compose version >/dev/null 2>&1; then
            docker compose build
            if [ $? -ne 0 ]; then
                echo "ERROR Docker build failed"
                exit 1
            fi

            echo "Starting Docker container..."
            docker compose up -d
            if [ $? -ne 0 ]; then
                echo "ERROR Docker startup failed"
                exit 1
            fi

            # Check health
            check_api_health

            if [ $? -eq 0 ]; then
                echo "🎉 API is running successfully!"
                echo "INFO Access the API at: http://localhost:8000"
                echo "📚 API documentation at: http://localhost:8000/docs"
                echo "🔍 To view logs: docker compose logs -f"
                echo "🛑 To stop: docker compose down"
            fi
        else
            echo "ERROR docker-compose is not installed. Install Docker Compose or use a Docker CLI that supports 'docker compose'."
            exit 1
        fi
    fi
}

# Function to run locally
run_locally() {
    echo "🖥️  Running locally..."
    
    # Check if virtual environment exists
    if [ ! -d ".venv" ]; then
        echo "📦 Creating virtual environment..."
        python -m venv .venv
    fi
    
    # Activate virtual environment
    echo "CONFIG Activating virtual environment..."
    source .venv/bin/activate
    
    # Install dependencies
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
    
    # Create necessary directories
    mkdir -p logs data/logs models
    
    # Check if model exists
    if [ ! -f "models/Random_Forest_final_model.joblib" ]; then
        echo "ERROR Model file not found. Please run the training notebook first."
        echo "Expected file: models/Random_Forest_final_model.joblib"
        exit 1
    fi
    
    # Set environment variables
    export PYTHONPATH="$(pwd)"
    export PYTHONUNBUFFERED=1
    
    # Start the API
    echo "Starting API server..."
    python src/serving/main.py &
    API_PID=$!
    
    # Wait a moment for startup
    sleep 3
    
    # Check health
    check_api_health
    
    if [ $? -eq 0 ]; then
        echo "🎉 API is running successfully!"
        echo "INFO Access the API at: http://localhost:8000"
        echo "📚 API documentation at: http://localhost:8000/docs"
        echo "🛑 To stop: kill $API_PID or Ctrl+C"
        
        # Keep the script running
        wait $API_PID
    else
        echo "ERROR API startup failed"
        kill $API_PID 2>/dev/null
        exit 1
    fi
}

# Function to run tests
run_tests() {
    echo "🧪 Running API tests..."
    
    # Check if API is running
    if ! curl -s -f http://localhost:8000/health > /dev/null 2>&1; then
        echo "ERROR API is not running. Please start the API first."
        exit 1
    fi
    
    # Run tests
    python -m pytest tests/ -q
}

# Function to stop services
stop_services() {
    echo "🛑 Stopping services..."
    
    # Stop Docker services
    if command -v docker-compose >/dev/null 2>&1; then
        docker-compose down
    elif docker compose version >/dev/null 2>&1; then
        docker compose down
    fi
    
    # Kill any local processes matching the API entry points
    pkill -f "uvicorn.*src.serving.main" || true
    pkill -f "python .*src/serving/main.py" || true
    
    echo "SUCCESS Services stopped"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start-local    Start API locally (default)"
    echo "  start-docker   Start API with Docker Compose"
    echo "  test           Run API tests"
    echo "  stop           Stop all services"
    echo "  help           Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start-local"
    echo "  $0 start-docker"
    echo "  $0 test"
    echo "  $0 stop"
}

# Parse command line arguments
case "${1:-start-local}" in
    "start-local")
        run_locally
        ;;
    "start-docker")
        run_with_docker
        ;;
    "test")
        run_tests
        ;;
    "stop")
        stop_services
        ;;
    "help"|"-h"|"--help")
        show_usage
        ;;
    *)
        echo "ERROR Unknown command: $1"
        show_usage
        exit 1
        ;;
esac
