#!/bin/bash

# =============================================================================
# MCP Server Template - Build Script (Linux/macOS)
# =============================================================================

set -euo pipefail

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
IMAGE_NAME="mcp-server-template"
REGISTRY=""
DEFAULT_TAG="latest"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
    exit 1
}

usage() {
    cat << EOF
🚀 MCP Server Template Build Script

Usage: $0 [OPTIONS]

OPTIONS:
    -t, --tag TAG           Docker image tag (default: $DEFAULT_TAG)
    -r, --registry URL      Docker registry URL
    -p, --push              Push image to registry
    -d, --dev               Build development image
    -e, --test              Build and run tests
    -c, --clean             Clean Docker cache and images
    -h, --help              Show this help message
    --no-cache              Build without Docker cache
    --platform PLATFORM     Target platform (e.g., linux/amd64,linux/arm64)

EXAMPLES:
    $0                      # Build production image with latest tag
    $0 -t v1.0.0 -p        # Build and push with tag v1.0.0
    $0 -d                   # Build development image
    $0 -e                   # Build and run tests
    $0 -c                   # Clean Docker cache
    $0 --platform linux/amd64,linux/arm64 -t v1.0.0 -p  # Multi-platform build

EOF
}

# Parse command line arguments
TAG="$DEFAULT_TAG"
PUSH=false
DEV=false
TEST=false
CLEAN=false
NO_CACHE=false
PLATFORM=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -t|--tag)
            TAG="$2"
            shift 2
            ;;
        -r|--registry)
            REGISTRY="$2"
            shift 2
            ;;
        -p|--push)
            PUSH=true
            shift
            ;;
        -d|--dev)
            DEV=true
            shift
            ;;
        -e|--test)
            TEST=true
            shift
            ;;
        -c|--clean)
            CLEAN=true
            shift
            ;;
        --no-cache)
            NO_CACHE=true
            shift
            ;;
        --platform)
            PLATFORM="$2"
            shift 2
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            error "Unknown option: $1"
            ;;
    esac
done

# Set full image name
if [[ -n "$REGISTRY" ]]; then
    FULL_IMAGE_NAME="$REGISTRY/$IMAGE_NAME:$TAG"
else
    FULL_IMAGE_NAME="$IMAGE_NAME:$TAG"
fi

# Change to project root
cd "$PROJECT_ROOT"

# Clean function
clean_docker() {
    log "🧹 Cleaning Docker cache and images..."
    
    # Remove dangling images
    docker image prune -f || true
    
    # Remove build cache
    docker builder prune -f || true
    
    # Remove project images
    docker images "$IMAGE_NAME" -q | xargs -r docker rmi -f || true
    
    success "Docker cleanup completed"
}

# Test function
run_tests() {
    log "🧪 Building test image and running tests..."
    
    docker build \
        -f docker/Dockerfile \
        --target testing \
        -t "$IMAGE_NAME:test" \
        . || error "Test image build failed"
    
    # Run tests
    docker run --rm \
        -v "$PROJECT_ROOT/coverage:/app/coverage" \
        "$IMAGE_NAME:test" || error "Tests failed"
    
    success "Tests completed successfully"
}

# Build function
build_image() {
    local target="production"
    local tag_suffix=""
    
    if [[ "$DEV" == true ]]; then
        target="development"
        tag_suffix="-dev"
    fi
    
    local image_tag="$IMAGE_NAME:$TAG$tag_suffix"
    
    log "🏗️  Building $target image: $image_tag"
    
    # Build command
    local build_cmd="docker build"
    local build_args=(
        "-f" "docker/Dockerfile"
        "--target" "$target"
        "-t" "$image_tag"
    )
    
    # Add no-cache if specified
    if [[ "$NO_CACHE" == true ]]; then
        build_args+=("--no-cache")
    fi
    
    # Add platform if specified
    if [[ -n "$PLATFORM" ]]; then
        build_args+=("--platform" "$PLATFORM")
    fi
    
    # Add context
    build_args+=(".")
    
    # Execute build
    $build_cmd "${build_args[@]}" || error "Build failed"
    
    success "Build completed: $image_tag"
    
    # Tag with registry name if different
    if [[ "$image_tag" != "$FULL_IMAGE_NAME" ]]; then
        docker tag "$image_tag" "$FULL_IMAGE_NAME"
        log "🏷️  Tagged as: $FULL_IMAGE_NAME"
    fi
}

# Push function
push_image() {
    log "📤 Pushing image to registry: $FULL_IMAGE_NAME"
    
    docker push "$FULL_IMAGE_NAME" || error "Push failed"
    
    success "Image pushed successfully"
}

# Verify Docker is running
if ! docker info > /dev/null 2>&1; then
    error "Docker is not running or not accessible"
fi

# Main execution
log "🚀 Starting MCP Server Template build process..."

# Execute requested operations
if [[ "$CLEAN" == true ]]; then
    clean_docker
fi

if [[ "$TEST" == true ]]; then
    run_tests
fi

if [[ "$CLEAN" != true ]] && [[ "$TEST" != true ]]; then
    build_image
fi

if [[ "$PUSH" == true ]]; then
    if [[ -z "$REGISTRY" ]]; then
        warning "No registry specified, skipping push"
    else
        push_image
    fi
fi

# Show final status
log "📊 Build Summary:"
echo "  • Image: $FULL_IMAGE_NAME"
echo "  • Target: $([ "$DEV" == true ] && echo "development" || echo "production")"
echo "  • Tests: $([ "$TEST" == true ] && echo "✅ Passed" || echo "⏭️  Skipped")"
echo "  • Push: $([ "$PUSH" == true ] && echo "✅ Completed" || echo "⏭️  Skipped")"

success "Build process completed successfully! 🎉"

# Show next steps
cat << EOF

🎯 Next Steps:
   • Run locally: docker run -p 8000:8000 $FULL_IMAGE_NAME
   • Start with compose: cd docker && docker-compose up
   • View logs: docker logs <container-name>
   • Test endpoint: curl http://localhost:8000/mcp

📚 Documentation: Check the README.md for more usage examples
EOF 