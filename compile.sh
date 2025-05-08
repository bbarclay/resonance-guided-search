#!/bin/bash

# compile.sh - A comprehensive LaTeX compilation script with error handling
# This script compiles the LaTeX document multiple times to resolve references,
# citations, and cross-references, and provides clear error notifications.

# Set the document name (without extension)
DOCUMENT="report"
TEX_DIR="docs/tex"
OUTPUT_DIR="docs/pdf"

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
}

# Function to print warning messages
print_warning() {
    echo -e "${YELLOW}! $1${NC}"
}

# Check if the tex directory exists
if [ ! -d "$TEX_DIR" ]; then
    print_error "LaTeX source directory $TEX_DIR does not exist!"
    exit 1
fi

# Check if the tex file exists
if [ ! -f "$TEX_DIR/$DOCUMENT.tex" ]; then
    print_error "LaTeX source file $TEX_DIR/$DOCUMENT.tex does not exist!"
    exit 1
fi

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

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
}

# Function to print warning messages
print_warning() {
    echo -e "${YELLOW}! $1${NC}"
}

# Function to check for LaTeX errors in the log file
check_errors() {
    if grep -q "^!" "$TEX_DIR/$DOCUMENT.log"; then
        print_error "LaTeX errors found in the compilation:"
        grep -A 2 "^!" "$TEX_DIR/$DOCUMENT.log"
        return 1
    fi
    return 0
}

# Function to check for undefined references
check_undefined_refs() {
    if grep -q "Reference.*undefined" "$TEX_DIR/$DOCUMENT.log"; then
        print_warning "Undefined references found:"
        grep "Reference.*undefined" "$TEX_DIR/$DOCUMENT.log"
        return 1
    fi
    return 0
}

# Function to check for undefined citations
check_undefined_citations() {
    if grep -q "Citation.*undefined" "$TEX_DIR/$DOCUMENT.log"; then
        print_warning "Undefined citations found:"
        grep "Citation.*undefined" "$TEX_DIR/$DOCUMENT.log"
        return 1
    fi
    return 0
}

# Function to check for other warnings
check_warnings() {
    if grep -q "Warning" "$TEX_DIR/$DOCUMENT.log"; then
        print_warning "Other warnings found:"
        grep "Warning" "$TEX_DIR/$DOCUMENT.log" | head -n 5
        if [ $(grep -c "Warning" "$TEX_DIR/$DOCUMENT.log") -gt 5 ]; then
            echo "... and $(( $(grep -c "Warning" "$TEX_DIR/$DOCUMENT.log") - 5 )) more warnings."
        fi
    fi
}

# Function to run pdflatex
run_pdflatex() {
    print_header "Running pdflatex (Pass $1)"
    cd "$TEX_DIR" || { print_error "Could not change to directory $TEX_DIR"; exit 1; }
    pdflatex -interaction=batchmode "$DOCUMENT.tex" > /dev/null
    local status=$?
    cd - > /dev/null || { print_error "Could not return from directory $TEX_DIR"; exit 1; }

    if [ $status -ne 0 ]; then
        print_error "pdflatex failed with exit code $status"
        return 1
    fi

    check_errors
    return $?
}

# Function to run bibtex
run_bibtex() {
    print_header "Running bibtex"
    cd "$TEX_DIR" || { print_error "Could not change to directory $TEX_DIR"; exit 1; }
    bibtex "$DOCUMENT" > /dev/null
    local status=$?
    cd - > /dev/null || { print_error "Could not return from directory $TEX_DIR"; exit 1; }

    if [ $status -ne 0 ]; then
        print_error "bibtex failed with exit code $status"
        return 1
    fi

    if grep -q "Warning--" "$TEX_DIR/$DOCUMENT.blg"; then
        print_warning "BibTeX warnings found:"
        grep "Warning--" "$TEX_DIR/$DOCUMENT.blg"
    fi

    return 0
}

# Main compilation process
print_header "Starting compilation of $DOCUMENT.tex"

# First pdflatex run
if ! run_pdflatex 1; then
    print_error "First pdflatex run failed. Aborting."
    exit 1
fi

# Run bibtex if citations are used
if grep -q "\\\\cite{" "$TEX_DIR/$DOCUMENT.tex" || grep -q "\\\\bibliography{" "$TEX_DIR/$DOCUMENT.tex" || grep -q "\\\\begin{thebibliography}" "$TEX_DIR/$DOCUMENT.tex"; then
    if ! run_bibtex; then
        print_error "BibTeX run failed. Continuing with compilation anyway."
    fi
fi

# Second pdflatex run to incorporate bibtex
if ! run_pdflatex 2; then
    print_error "Second pdflatex run failed. Aborting."
    exit 1
fi

# Third pdflatex run to resolve references
if ! run_pdflatex 3; then
    print_error "Third pdflatex run failed. Aborting."
    exit 1
fi

# Check for undefined references and citations after final run
undefined_refs=0
undefined_citations=0
check_undefined_refs || undefined_refs=1
check_undefined_citations || undefined_citations=1
check_warnings

# Copy the final PDF to the output directory
cp "$TEX_DIR/$DOCUMENT.pdf" "$OUTPUT_DIR/"
if [ $? -eq 0 ]; then
    print_success "PDF successfully generated and copied to $OUTPUT_DIR/$DOCUMENT.pdf"
else
    print_error "Failed to copy PDF to output directory"
    exit 1
fi

# Final status report
print_header "Compilation Summary"
if [ $undefined_refs -eq 0 ] && [ $undefined_citations -eq 0 ]; then
    print_success "Compilation completed successfully with no undefined references or citations."
    echo -e "\nYou can find the compiled PDF at: $OUTPUT_DIR/$DOCUMENT.pdf\n"
    exit 0
else
    if [ $undefined_refs -eq 1 ]; then
        print_warning "Compilation completed with undefined references."
    fi
    if [ $undefined_citations -eq 1 ]; then
        print_warning "Compilation completed with undefined citations."
    fi
    echo -e "\nYou can find the compiled PDF at: $OUTPUT_DIR/$DOCUMENT.pdf\n"
    echo -e "Consider running the script again to resolve all references and citations.\n"
    exit 0
fi
