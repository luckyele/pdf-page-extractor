import argparse
import re
from pathlib import Path
from typing import List, Union
import PyPDF2


def parse_page_ranges(ranges_str: str, total_pages: int) -> List[int]:
    pages = []
    parts = ranges_str.split(',')
    
    for part in parts:
        part = part.strip()
        if not part:
            continue
        
        if '-' in part:
            start_end = part.split('-')
            if len(start_end) != 2:
                raise ValueError(f"Invalid range format: {part}")
            
            start_str = start_end[0].strip()
            end_str = start_end[1].strip()
            
            start = int(start_str) if start_str else 1
            end = int(end_str) if end_str else total_pages
            
            if start < 1 or end > total_pages or start > end:
                raise ValueError(f"Invalid page range: {part}")
            
            pages.extend(range(start, end + 1))
        else:
            page = int(part)
            if page < 1 or page > total_pages:
                raise ValueError(f"Page {page} is out of range (1-{total_pages})")
            pages.append(page)
    
    return sorted(list(set(pages)))


def extract_even_pages(total_pages: int) -> List[int]:
    return [i for i in range(1, total_pages + 1) if i % 2 == 0]


def extract_odd_pages(total_pages: int) -> List[int]:
    return [i for i in range(1, total_pages + 1) if i % 2 == 1]


def extract_pages_by_interval(total_pages: int, start: int, interval: int) -> List[int]:
    return [i for i in range(start, total_pages + 1, interval)]


def extract_pages_by_regex(total_pages: int, pattern: str) -> List[int]:
    pages = []
    for i in range(1, total_pages + 1):
        if re.search(pattern, str(i)):
            pages.append(i)
    return pages


def extract_pages_from_file(file_path: str, total_pages: int) -> List[int]:
    pages = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and line.isdigit():
                page = int(line)
                if 1 <= page <= total_pages:
                    pages.append(page)
    return sorted(list(set(pages)))


def batch_extract_from_file(input_path: str, file_path: str, output_prefix: str, total_pages: int) -> None:
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]
    
    for idx, line in enumerate(lines, 1):
        try:
            pages = parse_page_ranges(line, total_pages)
            if not pages:
                print(f"Warning: Line {idx} has no valid pages: {line}")
                continue
            
            output_path = f"{output_prefix}_{idx:02d}.pdf"
            extract_pdf_pages(input_path, output_path, pages)
            print(f"File {idx}: extracted pages {line} -> {output_path} ({len(pages)} pages)")
        except ValueError as e:
            print(f"Error: Invalid format on line {idx} '{line}': {e}")


def extract_pdf_pages(input_path: str, output_path: str, pages: List[int]) -> None:
    with open(input_path, 'rb') as input_file:
        reader = PyPDF2.PdfReader(input_file)
        writer = PyPDF2.PdfWriter()
        
        for page_num in pages:
            writer.add_page(reader.pages[page_num - 1])
        
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)


def get_total_pages(input_path: str) -> int:
    with open(input_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        return len(reader.pages)


def main():
    parser = argparse.ArgumentParser(
        description='PDF Page Extractor - Extract pages from PDF in various ways',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract specific pages
  python pdf_extract.py input.pdf output.pdf --pages 1,3,5
  
  # Extract page ranges
  python pdf_extract.py input.pdf output.pdf --pages 1-5,10-15
  
  # Extract even pages
  python pdf_extract.py input.pdf output.pdf --even
  
  # Extract odd pages
  python pdf_extract.py input.pdf output.pdf --odd
  
  # Extract by interval (start from page 1, every 3 pages)
  python pdf_extract.py input.pdf output.pdf --interval 1 3
  
  # Use regex to match page numbers
  python pdf_extract.py input.pdf output.pdf --regex "1.*"
  
  # Read page list from file
  python pdf_extract.py input.pdf output.pdf --file pages.txt
  
  # Batch mode: each line generates a separate file
  python pdf_extract.py input.pdf output --batch pages.txt
        """
    )
    
    parser.add_argument('input', help='Input PDF file path')
    parser.add_argument('output', help='Output PDF file path')
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--pages', help='Specify pages, format: 1,3,5 or 1-5,10-15')
    group.add_argument('--even', action='store_true', help='Extract all even pages')
    group.add_argument('--odd', action='store_true', help='Extract all odd pages')
    group.add_argument('--interval', nargs=2, metavar=('START', 'INTERVAL'), 
                       help='Extract by interval, from START, every INTERVAL pages')
    group.add_argument('--regex', help='Use regex to match page numbers')
    group.add_argument('--file', help='Read page list from file (one page per line)')
    group.add_argument('--batch', metavar='PAGES_FILE', 
                       help='Batch mode: read each line as page range, generate separate files')
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    output_path = Path(args.output)
    
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}")
        return 1
    
    if input_path.suffix.lower() != '.pdf':
        print(f"Error: Input file must be PDF format")
        return 1
    
    try:
        total_pages = get_total_pages(str(input_path))
    except Exception as e:
        print(f"Error: Cannot read PDF file: {e}")
        return 1
    
    print(f"Total pages: {total_pages}")
    
    try:
        if args.pages:
            pages = parse_page_ranges(args.pages, total_pages)
            print(f"Extracting pages: {pages}")
        elif args.even:
            pages = extract_even_pages(total_pages)
            print(f"Extracting even pages: {pages}")
        elif args.odd:
            pages = extract_odd_pages(total_pages)
            print(f"Extracting odd pages: {pages}")
        elif args.interval:
            start = int(args.interval[0])
            interval = int(args.interval[1])
            pages = extract_pages_by_interval(total_pages, start, interval)
            print(f"Extracting by interval (from {start}, every {interval} pages): {pages}")
        elif args.regex:
            pages = extract_pages_by_regex(total_pages, args.regex)
            print(f"Pages matching regex '{args.regex}': {pages}")
        elif args.file:
            file_path = Path(args.file)
            if not file_path.exists():
                print(f"Error: Page file not found: {file_path}")
                return 1
            pages = extract_pages_from_file(args.file, total_pages)
            print(f"Pages from file: {pages}")
        elif args.batch:
            file_path = Path(args.batch)
            if not file_path.exists():
                print(f"Error: Page file not found: {file_path}")
                return 1
            output_prefix = str(output_path).replace('.pdf', '')
            batch_extract_from_file(str(input_path), args.batch, output_prefix, total_pages)
            print(f"Batch extraction complete!")
            return 0
        else:
            print("Error: Must specify a page extraction method")
            return 1
        
        if not pages:
            print("Error: No pages selected")
            return 1
        
        extract_pdf_pages(str(input_path), str(output_path), pages)
        print(f"Success! Extracted {len(pages)} pages to: {output_path}")
        
    except ValueError as e:
        print(f"Error: {e}")
        return 1
    except Exception as e:
        print(f"Error: Exception while processing PDF: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
