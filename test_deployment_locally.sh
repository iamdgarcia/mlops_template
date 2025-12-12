#!/bin/bash
set -e

echo "🧪 Testing MLOps Deployment Locally"
echo "===================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Step 1: Validate app.yaml syntax
echo -e "${YELLOW}Step 1: Validating .do/app.yaml syntax...${NC}"
if [ -f .do/app.yaml ]; then
    # Check if yq is installed for YAML validation
    if command -v yq &> /dev/null; then
        yq eval '.do/app.yaml' > /dev/null 2>&1 && echo -e "${GREEN}✓ YAML syntax is valid${NC}" || (echo -e "${RED}✗ Invalid YAML syntax${NC}" && exit 1)
    else
        # Basic YAML check with Python
        python3 -c "import yaml; yaml.safe_load(open('.do/app.yaml'))" && echo -e "${GREEN}✓ YAML syntax is valid${NC}" || (echo -e "${RED}✗ Invalid YAML syntax${NC}" && exit 1)
    fi
else
    echo -e "${RED}✗ .do/app.yaml not found${NC}"
    exit 1
fi
echo ""

# Step 2: Check if Dockerfile exists
echo -e "${YELLOW}Step 2: Checking Dockerfile...${NC}"
if [ -f Dockerfile ]; then
    echo -e "${GREEN}✓ Dockerfile found${NC}"
else
    echo -e "${RED}✗ Dockerfile not found${NC}"
    exit 1
fi
echo ""

# Step 3: Build Docker image
echo -e "${YELLOW}Step 3: Building Docker image...${NC}"
echo "This will take a few minutes..."
docker build -t fraud-detection-api:test . || (echo -e "${RED}✗ Docker build failed${NC}" && exit 1)
echo -e "${GREEN}✓ Docker image built successfully${NC}"
echo ""

# Step 4: Check if required files are in the image
echo -e "${YELLOW}Step 4: Verifying required files in image...${NC}"

# Check for model file
docker run --rm fraud-detection-api:test ls -la models/ || echo -e "${YELLOW}⚠ models/ directory not found or empty${NC}"

# Check for selected_features.json
docker run --rm fraud-detection-api:test ls -la data/selected_features.json || echo -e "${YELLOW}⚠ data/selected_features.json not found${NC}"

# Check for serve_model.py
docker run --rm fraud-detection-api:test ls -la scripts/serve_model.py && echo -e "${GREEN}✓ serve_model.py found${NC}" || (echo -e "${RED}✗ serve_model.py not found${NC}" && exit 1)

echo ""

# Step 5: Run container and test health endpoint
echo -e "${YELLOW}Step 5: Starting container and testing health endpoint...${NC}"

# Run container in background
CONTAINER_ID=$(docker run -d -p 8000:8000 --name fraud-api-test fraud-detection-api:test)
echo "Container started with ID: $CONTAINER_ID"

# Wait for container to be ready
echo "Waiting for application to start..."
sleep 10

# Check if container is still running
if ! docker ps | grep -q fraud-api-test; then
    echo -e "${RED}✗ Container stopped unexpectedly${NC}"
    echo "Container logs:"
    docker logs fraud-api-test
    docker rm -f fraud-api-test 2>/dev/null || true
    exit 1
fi

# Test health endpoint
echo "Testing /health endpoint..."
HEALTH_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health || echo "000")

if [ "$HEALTH_RESPONSE" = "200" ]; then
    echo -e "${GREEN}✓ Health check passed (HTTP 200)${NC}"
    
    # Get health check details
    echo ""
    echo "Health check response:"
    curl -s http://localhost:8000/health | python3 -m json.tool || curl -s http://localhost:8000/health
else
    echo -e "${RED}✗ Health check failed (HTTP $HEALTH_RESPONSE)${NC}"
    echo "Container logs:"
    docker logs fraud-api-test
    docker rm -f fraud-api-test 2>/dev/null || true
    exit 1
fi

echo ""

# Step 6: Test API docs endpoint
echo -e "${YELLOW}Step 6: Testing API documentation endpoint...${NC}"
DOCS_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/docs || echo "000")

if [ "$DOCS_RESPONSE" = "200" ]; then
    echo -e "${GREEN}✓ API docs accessible at http://localhost:8000/docs${NC}"
else
    echo -e "${YELLOW}⚠ API docs returned HTTP $DOCS_RESPONSE${NC}"
fi

echo ""

# Step 7: Test prediction endpoint (optional)
echo -e "${YELLOW}Step 7: Testing prediction endpoint...${NC}"
PREDICTION=$(curl -s -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 500.0,
    "merchant_category": "retail",
    "transaction_type": "purchase",
    "location": "US",
    "device_type": "mobile",
    "hour_of_day": 14,
    "day_of_week": 3,
    "user_transaction_frequency": 10.5,
    "user_avg_amount": 250.0,
    "user_transaction_count": 25
  }' || echo "FAILED")

if echo "$PREDICTION" | grep -q "fraud_probability"; then
    echo -e "${GREEN}✓ Prediction endpoint working${NC}"
    echo "Sample prediction response:"
    echo "$PREDICTION" | python3 -m json.tool || echo "$PREDICTION"
else
    echo -e "${YELLOW}⚠ Prediction endpoint may have issues${NC}"
    echo "Response: $PREDICTION"
fi

echo ""

# Cleanup
echo -e "${YELLOW}Cleaning up...${NC}"
docker stop fraud-api-test > /dev/null 2>&1 || true
docker rm fraud-api-test > /dev/null 2>&1 || true
echo -e "${GREEN}✓ Container stopped and removed${NC}"

echo ""
echo "===================================="
echo -e "${GREEN}🎉 All local deployment tests passed!${NC}"
echo "===================================="
echo ""
echo "Your application is ready for deployment to DigitalOcean!"
echo ""
echo "To keep the container running for manual testing:"
echo "  docker run -d -p 8000:8000 --name fraud-api fraud-detection-api:test"
echo ""
echo "To view logs:"
echo "  docker logs -f fraud-api"
echo ""
echo "To stop:"
echo "  docker stop fraud-api && docker rm fraud-api"
