---
name: pdf-page-extractor
description: Extract pages from PDF documents using various methods including specific pages, ranges, even/odd pages, intervals, regex patterns, or batch processing. Use when the user needs to (1) Extract specific pages from a PDF, (2) Split PDF by page ranges, (3) Extract even or odd pages, (4) Extract pages at regular intervals, (5) Batch extract multiple page ranges into separate files, or (6) Any PDF page extraction task.
---

# PDF Page Extractor

Extract pages from PDF documents using flexible selection methods.

## Quick Start

Use the script directly:

```bash
python scripts/pdf_extract.py input.pdf output.pdf --pages 1,3,5-10
```

## Extraction Methods

### 1. Specific Pages

Extract individual pages:

```bash
python scripts/pdf_extract.py input.pdf output.pdf --pages 1,3,5,7
```

### 2. Page Ranges

Extract continuous ranges (combine with individual pages):

```bash
python scripts/pdf_extract.py input.pdf output.pdf --pages 1-5,10-15,20
```

### 3. Even/Odd Pages

```bash
# Extract all even pages
python scripts/pdf_extract.py input.pdf output.pdf --even

# Extract all odd pages
python scripts/pdf_extract.py input.pdf output.pdf --odd
```

### 4. Interval Extraction

Extract pages at regular intervals:

```bash
# From page 1, extract every 3rd page (1, 4, 7, 10, ...)
python scripts/pdf_extract.py input.pdf output.pdf --interval 1 3

# From page 2, extract every 5th page (2, 7, 12, 17, ...)
python scripts/pdf_extract.py input.pdf output.pdf --interval 2 5
```

### 5. Regex Pattern Matching

Extract pages whose numbers match a regex:

```bash
# Pages starting with 1 (1, 10-19, 100-199, etc.)
python scripts/pdf_extract.py input.pdf output.pdf --regex "1.*"

# Pages ending with 5 (5, 15, 25, 35, ...)
python scripts/pdf_extract.py input.pdf output.pdf --regex "5$"
```

### 6. From File

Read page numbers from a text file (one per line):

```bash
python scripts/pdf_extract.py input.pdf output.pdf --file pages.txt
```

### 7. Batch Mode

Generate multiple PDFs from a single file. Each line in the file specifies a page range:

```bash
python scripts/pdf_extract.py input.pdf output --batch ranges.txt
```

Example `ranges.txt`:
```
1-5
10-15
20,25,30
```

This creates: `output_01.pdf`, `output_02.pdf`, `output_03.pdf`

## Programmatic Usage

Import functions directly in Python:

```python
from scripts.pdf_extract import (
    extract_pdf_pages,
    parse_page_ranges,
    extract_even_pages,
    extract_odd_pages,
    extract_pages_by_interval,
    get_total_pages
)

# Get page count
total = get_total_pages("input.pdf")

# Parse page range string
pages = parse_page_ranges("1-5,10,15-20", total)

# Extract pages
extract_pdf_pages("input.pdf", "output.pdf", pages)
```

## Requirements

- Python 3.7+
- PyPDF2 library

Install dependency:
```bash
pip install PyPDF2
```
