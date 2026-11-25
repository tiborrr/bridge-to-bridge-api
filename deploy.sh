#!/bin/bash

# Deploy script for bridge-to-bridge-api
# Builds the Docker images, pushes them to the registry and deploys them on the production
# server, which is this machine (omarchy): the compose project lives in DEPLOY_PATH.

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Configuration
export IMAGE_TAG="v$(date +%Y%m%d%H%M%S)"
export DOCKER_DEFAULT_PLATFORM=linux/amd64
DEPLOY_PATH="${DEPLOY_PATH:-$HOME/deployments/brug-tot-brug}"

command_exists() { command -v "$1" >/dev/null 2>&1; }

check_dependencies() {
    print_status "Checking dependencies..."
    if ! command_exists docker; then print_error "Docker is not installed or not in PATH"; exit 1; fi
    if ! command_exists rsync; then print_error "rsync is not installed or not in PATH"; exit 1; fi
    if [ ! -f "${DEPLOY_PATH}/.env" ]; then print_error "${DEPLOY_PATH}/.env not found; is this the production server?"; exit 1; fi
    print_success "All dependencies are available"
}

build_images() {
    print_status "Building Docker images with tag ${IMAGE_TAG}..."
    docker compose build -q
    print_success "Docker images built successfully"
}

push_images() {
    print_status "Pushing Docker images to registry..."
    docker compose push -q
    print_success "Docker images pushed successfully"
}

sync_config() {
    print_status "Syncing configuration to ${DEPLOY_PATH}"
    # The production .env holds the secrets and is never overwritten; only IMAGE_TAG is updated,
    # so a plain `docker compose` in DEPLOY_PATH keeps using the deployed images.
    rsync -aR "docker-compose.yml" "keycloak/realm-config" "${DEPLOY_PATH}/"
    if grep -q '^IMAGE_TAG=' "${DEPLOY_PATH}/.env"; then
        sed -i "s/^IMAGE_TAG=.*/IMAGE_TAG=${IMAGE_TAG}/" "${DEPLOY_PATH}/.env"
    else
        echo "IMAGE_TAG=${IMAGE_TAG}" >> "${DEPLOY_PATH}/.env"
    fi
    print_success "Configuration synced; IMAGE_TAG=${IMAGE_TAG} in ${DEPLOY_PATH}/.env"
}

deploy() {
    print_status "Recreating api and bridge-keycloak with ${IMAGE_TAG}..."
    (cd "${DEPLOY_PATH}" && docker compose up -d --no-deps bridge-keycloak api && docker compose ps)
    print_status "Cleaning up dangling images..."
    docker image prune -f
    print_success "Deployment completed!"
}

cleanup_registry() {
    print_status "Cleaning up old images from registry..."
    
    if ! command_exists jq; then
        print_warning "jq is not installed. Skipping registry cleanup."
        return
    fi
    
    local config_file="$HOME/.docker/config.json"
    if [ ! -f "$config_file" ]; then
        print_warning "Docker config not found. Skipping registry cleanup."
        return
    fi
    
    local auth=""
    local creds_store=$(jq -r '.credsStore // empty' "$config_file")
    if [ -n "$creds_store" ] && command_exists "docker-credential-$creds_store"; then
        local creds_json=$(echo "registry.casteleijn.com" | "docker-credential-$creds_store" get 2>/dev/null || echo "")
        local user=$(echo "$creds_json" | jq -r '.Username // empty')
        local secret=$(echo "$creds_json" | jq -r '.Secret // empty')
        if [ -n "$user" ] && [ -n "$secret" ]; then
            auth=$(echo -n "${user}:${secret}" | base64)
        fi
    fi
    
    if [ -z "$auth" ]; then
        auth=$(jq -r '.auths["registry.casteleijn.com"].auth // empty' "$config_file")
    fi
    
    if [ -z "$auth" ]; then
        print_warning "No auth token found for registry.casteleijn.com in Docker config. Skipping cleanup."
        return
    fi
    
    local repos=("bridge-api" "bridge-api-keycloak")
    local keep=3
    
    for repo in "${repos[@]}"; do
        print_status "Cleaning up ${repo}..."
        local tags_json=$(curl -s -H "Authorization: Basic $auth" "https://registry.casteleijn.com/v2/${repo}/tags/list")
        
        # Check if tags is null or empty
        local has_tags=$(echo "$tags_json" | jq -e '.tags != null')
        if [ "$has_tags" != "true" ]; then
            continue
        fi
        
        local tags=($(echo "$tags_json" | jq -r '.tags[] | select(. != "latest")' | sort))
        
        if [ ${#tags[@]} -le $keep ]; then
            print_status "Found ${#tags[@]} tags. Keeping all."
            continue
        fi
        
        local delete_count=$((${#tags[@]} - keep))
        for (( i=0; i<$delete_count; i++ )); do
            local tag="${tags[$i]}"
            print_status "Deleting old tag: ${tag}"
            
            # Get digest
            local digest=$(curl -s -I -H "Authorization: Basic $auth" \
                -H "Accept: application/vnd.docker.distribution.manifest.v2+json" \
                -H "Accept: application/vnd.docker.distribution.manifest.list.v2+json" \
                -H "Accept: application/vnd.oci.image.manifest.v1+json" \
                -H "Accept: application/vnd.oci.image.index.v1+json" \
                "https://registry.casteleijn.com/v2/${repo}/manifests/${tag}" | grep -i "^Docker-Content-Digest:" | awk '{print $2}' | tr -d '\r')
                
            if [ -n "$digest" ]; then
                curl -s -X DELETE -H "Authorization: Basic $auth" "https://registry.casteleijn.com/v2/${repo}/manifests/${digest}" > /dev/null
                print_success "Deleted ${repo}:${tag}"
            else
                print_warning "Could not get digest for ${tag}"
            fi
        done
    done
}

show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --no-deploy      Build, push and sync config, but do not recreate containers"
    echo "  --help          Show this help message"
}

SKIP_DEPLOY=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --no-deploy) SKIP_DEPLOY=true; shift ;;
        --help) show_usage; exit 0 ;;
        *) print_error "Unknown option: $1"; show_usage; exit 1 ;;
    esac
done

main() {
    print_status "Starting deployment process..."
    print_status "Target Tag: ${IMAGE_TAG}"
    print_status "Deploy path: ${DEPLOY_PATH}"
    
    check_dependencies
    build_images
    push_images
    sync_config

    if [ "$SKIP_DEPLOY" = false ]; then
        deploy
    else
        print_status "Manual deployment required:"
        print_status "  cd ${DEPLOY_PATH} && docker compose up -d --no-deps bridge-keycloak api"
    fi
    
    cleanup_registry
    print_success "Deployment process completed!"
}

main "$@"
