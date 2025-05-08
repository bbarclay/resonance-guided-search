#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print section headers
print_header() {
    echo -e "\n${BLUE}=== $1 ===${NC}\n"
}

# Function to print success messages
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Function to print error messages
print_error() {
    echo -e "${RED}✗ $1${NC}"
    exit 1
}

# Function to print warning messages
print_warning() {
    echo -e "${YELLOW}! $1${NC}"
}

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    print_error "GitHub CLI (gh) is not installed. Please install it from https://cli.github.com/"
fi

# Check if git is installed
if ! command -v git &> /dev/null; then
    print_error "Git is not installed. Please install it from https://git-scm.com/"
fi

# Repository name
REPO_NAME="resonance-guided-search"
DESCRIPTION="A novel heuristic framework for pathfinding and optimization based on adaptability in conserved systems"
TOPICS="pathfinding,optimization,heuristics,adaptability,a-star,search-algorithms,mathematical-framework,python,visualization,machine-learning"

print_header "Creating GitHub Repository"
echo "Repository Name: $REPO_NAME"
echo "Description: $DESCRIPTION"
echo "Topics: $TOPICS"

# Create the repository
print_header "Creating repository on GitHub"
gh repo create "$REPO_NAME" --public --description "$DESCRIPTION" || print_error "Failed to create repository"
print_success "Repository created successfully"

# Initialize git repository
print_header "Initializing local git repository"
git init || print_error "Failed to initialize git repository"
print_success "Git repository initialized"

# Add all files
print_header "Adding files to git repository"
git add . || print_error "Failed to add files"
print_success "Files added successfully"

# Commit changes
print_header "Committing changes"
git commit -m "Initial commit: Resonance-Guided Search Framework" || print_error "Failed to commit changes"
print_success "Changes committed successfully"

# Add remote
print_header "Adding remote repository"
git remote add origin "https://github.com/$(gh api user | jq -r '.login')/$REPO_NAME.git" || print_error "Failed to add remote"
print_success "Remote added successfully"

# Push to GitHub
print_header "Pushing to GitHub"
git push -u origin main || print_error "Failed to push to GitHub"
print_success "Code pushed successfully"

# Add topics
print_header "Adding topics to repository"
gh api "repos/$(gh api user | jq -r '.login')/$REPO_NAME/topics" -X PUT -f "names=$TOPICS" || print_warning "Failed to add topics"
print_success "Topics added successfully"

# Enable GitHub Pages
print_header "Enabling GitHub Pages"
gh api "repos/$(gh api user | jq -r '.login')/$REPO_NAME/pages" -X POST -f "source[branch]=main" -f "source[path]=/docs" || print_warning "Failed to enable GitHub Pages"
print_success "GitHub Pages enabled successfully"

print_header "Repository Setup Complete"
echo "Repository URL: https://github.com/$(gh api user | jq -r '.login')/$REPO_NAME"
echo "GitHub Pages URL: https://$(gh api user | jq -r '.login').github.io/$REPO_NAME"
echo ""
print_success "Your Resonance-Guided Search Framework is now live on GitHub!"
