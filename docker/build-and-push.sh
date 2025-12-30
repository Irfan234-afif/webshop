#!/bin/bash
# Docker Hub Build and Push Script
# Repository: irfan33/koperasi-webshop (PRIVATE)

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Docker Hub Build & Push ===${NC}"
echo "Repository: irfan33/koperasi-webshop"
echo ""

# Step 1: Login to Docker Hub
echo -e "${BLUE}Step 1: Login to Docker Hub${NC}"
docker login
echo ""

# Step 2: Build image
echo -e "${BLUE}Step 2: Building Docker image${NC}"
cd "$(dirname "$0")/.."  # Go to webshop root

# Get git commit hash for versioning
GIT_SHA=$(git rev-parse --short HEAD 2>/dev/null || echo "local")
VERSION="v1.0.0"

docker build \
  -f docker/Containerfile \
  -t irfan33/koperasi-webshop:latest \
  -t irfan33/koperasi-webshop:${VERSION} \
  -t irfan33/koperasi-webshop:${GIT_SHA} \
  .

echo -e "${GREEN}✅ Build completed!${NC}"
echo ""

# Step 3: Push to Docker Hub
echo -e "${BLUE}Step 3: Pushing to Docker Hub${NC}"
docker push irfan33/koperasi-webshop:latest
docker push irfan33/koperasi-webshop:${VERSION}
docker push irfan33/koperasi-webshop:${GIT_SHA}

echo ""
echo -e "${GREEN}✅ Successfully pushed to Docker Hub!${NC}"
echo ""
echo "Images available at:"
echo "  - irfan33/koperasi-webshop:latest"
echo "  - irfan33/koperasi-webshop:${VERSION}"
echo "  - irfan33/koperasi-webshop:${GIT_SHA}"
