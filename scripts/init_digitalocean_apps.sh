#!/bin/bash

################################################################################
# DigitalOcean App Platform Initialization Script
################################################################################
# This script creates three app environments for the fraud detection API:
# 1. Production (fraud-detection-api)
# 2. Staging (fraud-detection-api-staging)
# 3. Development (fraud-detection-api-dev)
#
# Prerequisites:
# - doctl CLI installed and authenticated
# - DIGITALOCEAN_ACCESS_TOKEN environment variable or doctl auth
# - GitHub repository connected to DigitalOcean
################################################################################

# Don't use set -e as we handle errors explicitly

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REPO_URL="${REPO_URL:-github.com/iamdgarcia/mlops_template}"
SPEC_FILE="${SPEC_FILE:-.do/app.yaml}"

################################################################################
# Helper Functions
################################################################################

print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

check_prerequisites() {
    print_header "Checking Prerequisites"
    
    # Check if doctl is installed
    if ! command -v doctl &> /dev/null; then
        print_error "doctl CLI is not installed"
        echo "Install it from: https://docs.digitalocean.com/reference/doctl/how-to/install/"
        exit 1
    fi
    print_success "doctl CLI installed"
    
    # Check if authenticated
    if ! doctl auth list &> /dev/null; then
        print_error "doctl is not authenticated"
        echo "Run: doctl auth init"
        exit 1
    fi
    print_success "doctl authenticated"
    
    # Check if spec file exists
    if [ ! -f "$SPEC_FILE" ]; then
        print_error "App spec file not found: $SPEC_FILE"
        exit 1
    fi
    print_success "App spec file found: $SPEC_FILE"
    
    # Validate spec file
    if ! doctl apps spec validate "$SPEC_FILE" &> /dev/null; then
        print_error "App spec validation failed"
        doctl apps spec validate "$SPEC_FILE"
        exit 1
    fi
    print_success "App spec is valid"
}

create_app() {
    local app_name=$1
    local branch=$2
    local environment=$3
    
    print_header "Creating $environment App: $app_name"
    
    # Check if app already exists
    if doctl apps list --format Name --no-header | grep -q "^${app_name}$"; then
        print_warning "App '$app_name' already exists"
        
        # Get existing app ID
        local app_id=$(doctl apps list --format ID,Name --no-header | grep "$app_name" | awk '{print $1}')
        print_warning "Found existing app ID: $app_id"
        
        # Ask if user wants to delete and recreate
        read -p "Delete and recreate this app? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_warning "Deleting existing app..."
            doctl apps delete "$app_id" --force
            if [ $? -eq 0 ]; then
                print_success "App deleted successfully"
                sleep 3  # Wait a bit for deletion to complete
            else
                print_error "Failed to delete app"
                return 1
            fi
        else
            print_warning "Skipping app creation. Using existing app ID."
            CREATED_APP_ID="$app_id"
            return 0
        fi
    fi
    
    # Create temporary spec file for new app
    local temp_spec="./tmp/${app_name}-spec.yaml"
    
    >&2 echo "Creating temporary spec: $temp_spec"
    
    # Use sed to create modified spec without in-place editing
    sed -e "s/name: fraud-detection-api/name: ${app_name}/" \
        -e "s/branch: master/branch: ${branch}/" \
        "$SPEC_FILE" > "$temp_spec" || {
        print_error "Failed to create spec file"
        return 1
    }
    
    # Verify temp spec exists and has content
    if [ ! -f "$temp_spec" ] || [ ! -s "$temp_spec" ]; then
        print_error "Temporary spec file is missing or empty: $temp_spec"
        return 1
    fi
    
    >&2 echo "Creating app with spec: $temp_spec"
    >&2 echo "Branch: $branch"
    
    # Debug: Check file before doctl
    if [ -f "$temp_spec" ]; then
        >&2 echo "✓ Temp spec file exists and is readable"
        >&2 ls -lh "$temp_spec"
    else
        print_error "Temp spec file disappeared: $temp_spec"
        return 1
    fi
    
    # Create the app - use the full path explicitly
    >&2 echo "Running: doctl apps create --spec $temp_spec"
    local app_id=$(doctl apps create --spec "$temp_spec" --format ID --no-header 2>&1)
    local create_status=$?
    
    >&2 echo "doctl exit status: $create_status"
    >&2 echo "doctl output: $app_id"
    
    # Clean up temp file
    rm -f "$temp_spec"
    
    if [ $create_status -ne 0 ] || [ -z "$app_id" ] || [[ "$app_id" == *"Error"* ]]; then
        print_error "Failed to create app $app_name: $app_id"
        return 1
    fi
    
    print_success "App created successfully"
    print_success "App ID: $app_id"
    
    # Return via global variable
    CREATED_APP_ID="$app_id"
    return 0
}

get_app_url() {
    local app_id=$1
    
    # Wait a bit for the app to be provisioned
    sleep 5
    
    # Get the live URL
    local url=$(doctl apps get "$app_id" --format LiveURL --no-header)
    
    if [ -z "$url" ]; then
        # Try to get default ingress
        url=$(doctl apps get "$app_id" --format DefaultIngress --no-header)
    fi
    
    echo "$url"
}

display_summary() {
    local prod_id=$1
    local prod_url=$2
    local staging_id=$3
    local staging_url=$4
    local dev_id=$5
    local dev_url=$6
    
    print_header "Deployment Summary"
    
    echo -e "${GREEN}✓ All apps created successfully!${NC}\n"
    
    echo "📦 Production App"
    echo "   Name: fraud-detection-api"
    echo "   ID:   $prod_id"
    echo "   URL:  https://$prod_url"
    echo "   Branch: master"
    echo ""
    
    echo "📦 Staging App"
    echo "   Name: fraud-detection-api-staging"
    echo "   ID:   $staging_id"
    echo "   URL:  https://$staging_url"
    echo "   Branch: staging"
    echo ""
    
    echo "📦 Development App"
    echo "   Name: fraud-detection-api-dev"
    echo "   ID:   $dev_id"
    echo "   URL:  https://$dev_url"
    echo "   Branch: develop"
    echo ""
    
    print_header "Next Steps"
    
    echo "1. Add GitHub Secrets to your repository:"
    echo "   Go to: https://github.com/${REPO_URL}/settings/secrets/actions"
    echo ""
    echo "   Required secrets:"
    echo "   - DIGITALOCEAN_ACCESS_TOKEN (you should already have this)"
    echo "   - PRODUCTION_APP_URL=https://$prod_url"
    echo "   - STAGING_APP_URL=https://$staging_url"
    echo "   - DEV_APP_URL=https://$dev_url"
    echo ""
    
    echo "2. Create the staging and develop branches if they don't exist:"
    echo "   git checkout -b staging && git push origin staging"
    echo "   git checkout -b develop && git push origin develop"
    echo "   git checkout master"
    echo ""
    
    echo "3. Push to master to trigger the first deployment:"
    echo "   git push origin master"
    echo ""
    
    echo "4. Monitor your deployments at:"
    echo "   https://cloud.digitalocean.com/apps"
    echo ""
    
    print_success "Setup complete! 🎉"
}

export_env_vars() {
    local prod_id=$1
    local prod_url=$2
    local staging_id=$3
    local staging_url=$4
    local dev_id=$5
    local dev_url=$6
    
    local env_file=".env.digitalocean"
    
    cat > "$env_file" << EOF
# DigitalOcean App Platform Configuration
# Generated: $(date)

# Production
PRODUCTION_APP_ID=$prod_id
PRODUCTION_APP_URL=https://$prod_url

# Staging
STAGING_APP_ID=$staging_id
STAGING_APP_URL=https://$staging_url

# Development
DEV_APP_ID=$dev_id
DEV_APP_URL=https://$dev_url

# Add these to your GitHub repository secrets:
# Settings -> Secrets and variables -> Actions -> New repository secret
EOF
    
    print_success "Environment variables saved to: $env_file"
}

################################################################################
# Main Script
################################################################################

main() {
    print_header "DigitalOcean App Platform Setup"
    echo "This script will create three apps:"
    echo "  1. Production (fraud-detection-api) - master branch"
    echo "  2. Staging (fraud-detection-api-staging) - staging branch"
    echo "  3. Development (fraud-detection-api-dev) - develop branch"
    echo ""
    
    read -p "Continue? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 0
    fi
    
    # Check prerequisites
    check_prerequisites
    
    # Create apps
    echo "Starting app creation..."
    
    create_app "fraud-detection-api" "master" "Production"
    if [ $? -ne 0 ]; then
        print_error "Failed to create production app. Exiting."
        exit 1
    fi
    PROD_ID="$CREATED_APP_ID"
    
    create_app "fraud-detection-api-staging" "staging" "Staging"
    if [ $? -ne 0 ]; then
        print_error "Failed to create staging app. Exiting."
        exit 1
    fi
    STAGING_ID="$CREATED_APP_ID"
    
    create_app "fraud-detection-api-dev" "develop" "Development"
    if [ $? -ne 0 ]; then
        print_error "Failed to create development app. Exiting."
        exit 1
    fi
    DEV_ID="$CREATED_APP_ID"
    
    # Get app URLs
    print_header "Retrieving App URLs"
    PROD_URL=$(get_app_url "$PROD_ID")
    STAGING_URL=$(get_app_url "$STAGING_ID")
    DEV_URL=$(get_app_url "$DEV_ID")
    
    print_success "URLs retrieved"
    
    # Export to env file
    export_env_vars "$PROD_ID" "$PROD_URL" "$STAGING_ID" "$STAGING_URL" "$DEV_ID" "$DEV_URL"
    
    # Display summary
    display_summary "$PROD_ID" "$PROD_URL" "$STAGING_ID" "$STAGING_URL" "$DEV_ID" "$DEV_URL"
}

# Run main function
main "$@"
