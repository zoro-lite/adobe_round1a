#!/usr/bin/env python3
"""
Adobe India Hackathon - Round 1A
PDF Outline Extractor

This solution extracts structured outlines from PDFs including:
- Document title
- Headings (H1, H2, H3) with hierarchy levels and page numbers

Approach:
1. Use PyMuPDF (fitz) for PDF text extraction and analysis
2. Analyze font sizes, styles, and formatting to identify headings
3. Use text patterns and positioning to determine heading hierarchy
4. Extract title from first page or document metadata
5. Output structured JSON format as required
"""

import fitz  # PyMuPDF
import json
import os
import re
from pathlib import Path
import sys
from typing import List, Dict, Any, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PDFOutlineExtractor:
    def __init__(self):
        self.heading_patterns = [
            # Common heading patterns
            r'^(?:chapter|section|part)\s*\d+',
            r'^\d+\.?\s+[A-Z]',
            r'^[A-Z][A-Z\s]{3,}$',  # ALL CAPS headings
            r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*$',  # Title Case
        ]
        
    def extract_text_with_formatting(self, page) -> List[Dict]:
        """Extract text with formatting information from a page"""
        blocks = page.get_text("dict")["blocks"]
        formatted_text = []
        
        for block in blocks:
            if "lines" in block:  # Text block
                for line in block["lines"]:
                    for span in line["spans"]:
                        if span["text"].strip():
                            formatted_text.append({
                                "text": span["text"].strip(),
                                "font_size": span["size"],
                                "font": span["font"],
                                "flags": span["flags"],  # bold, italic flags
                                "bbox": span["bbox"],
                                "page": page.number + 1
                            })
        
        return formatted_text
    
    def is_bold(self, flags: int) -> bool:
        """Check if text is bold based on flags"""
        return bool(flags & 2**4)
    
    def is_title_candidate(self, text: str, font_size: float, is_bold: bool, page_num: int) -> bool:
        """Determine if text could be a document title"""
        if page_num > 2:  # Titles are usually on first 2 pages
            return False
        
        # Title characteristics
        if len(text) < 5 or len(text) > 200:
            return False
            
        # Check for title-like patterns
        title_indicators = [
            not text.isupper() or len(text) < 50,  # Not all caps unless short
            any(word in text.lower() for word in ['introduction', 'overview', 'guide', 'manual', 'report']),
            font_size > 14,  # Larger font
            is_bold
        ]
        
        return sum(title_indicators) >= 2
    
    def determine_heading_level(self, text: str, font_size: float, is_bold: bool, 
                              avg_font_size: float, max_font_size: float) -> str:
        """Determine heading level based on font size and formatting"""
        
        # Relative font size thresholds
        size_ratio = font_size / avg_font_size if avg_font_size > 0 else 1
        
        # Level determination based on font size relative to document average
        if size_ratio >= 1.8 or font_size >= max_font_size * 0.9:
            return "H1"
        elif size_ratio >= 1.4 or font_size >= max_font_size * 0.7:
            return "H2"
        elif size_ratio >= 1.2 or font_size >= max_font_size * 0.6:
            return "H3"
        elif is_bold and size_ratio >= 1.1:
            return "H3"
        
        return None
    
    def is_heading_by_pattern(self, text: str) -> bool:
        """Check if text matches common heading patterns"""
        text_clean = text.strip()
        
        # Check various heading patterns
        patterns_to_check = [
            r'^\d+\.?\s+[A-Z]',  # "1. Introduction" or "1 Introduction"
            r'^Chapter\s+\d+',   # "Chapter 1"
            r'^Section\s+\d+',   # "Section 1"
            r'^Part\s+[IVX]+',   # "Part I", "Part II"
            r'^[A-Z][A-Z\s]{5,}$',  # ALL CAPS (longer than 5 chars)
            r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*[.:]?$',  # Title Case
            r'^\d+\.\d+',        # "1.1", "2.3" etc
        ]
        
        for pattern in patterns_to_check:
            if re.match(pattern, text_clean, re.IGNORECASE):
                return True
        
        # Additional checks
        if (len(text_clean.split()) <= 8 and  # Not too long
            text_clean[0].isupper() and  # Starts with capital
            not text_clean.endswith(('.', '!', '?')) and  # Not a sentence
            len(text_clean) > 3):  # Not too short
            return True
            
        return False
    
    def extract_title(self, doc) -> str:
        """Extract document title from metadata or first page"""
        
        # Try metadata first
        metadata = doc.metadata
        if metadata.get('title') and len(metadata['title'].strip()) > 0:
            title = metadata['title'].strip()
            if len(title) > 5 and len(title) < 200:
                return title
        
        # Extract from first few pages
        potential_titles = []
        
        for page_num in range(min(3, len(doc))):
            page = doc[page_num]
            formatted_text = self.extract_text_with_formatting(page)
            
            if not formatted_text:
                continue
                
            # Calculate font statistics for this page
            font_sizes = [item["font_size"] for item in formatted_text]
            if not font_sizes:
                continue
                
            avg_font_size = sum(font_sizes) / len(font_sizes)
            max_font_size = max(font_sizes)
            
            for item in formatted_text:
                text = item["text"].strip()
                font_size = item["font_size"]
                is_bold = self.is_bold(item["flags"])
                
                if self.is_title_candidate(text, font_size, is_bold, page_num + 1):
                    potential_titles.append({
                        "text": text,
                        "font_size": font_size,
                        "page": page_num + 1,
                        "score": font_size + (10 if is_bold else 0) + (5 if page_num == 0 else 0)
                    })
        
        if potential_titles:
            # Return the highest scoring title
            best_title = max(potential_titles, key=lambda x: x["score"])
            return best_title["text"]
        
        # Fallback: use filename without extension
        return "Document"
    
    def extract_outline(self, pdf_path: str) -> Dict[str, Any]:
        """Extract structured outline from PDF"""
        logger.info(f"Processing PDF: {pdf_path}")
        
        try:
            doc = fitz.open(pdf_path)
        except Exception as e:
            logger.error(f"Error opening PDF {pdf_path}: {str(e)}")
            return {"title": "Error", "outline": []}
        
        # Extract title
        title = self.extract_title(doc)
        logger.info(f"Extracted title: {title}")
        
        # Extract headings
        outline = []
        all_formatted_text = []
        
        # First pass: collect all formatted text
        for page_num in range(len(doc)):
            page = doc[page_num]
            formatted_text = self.extract_text_with_formatting(page)
            all_formatted_text.extend(formatted_text)
        
        if not all_formatted_text:
            doc.close()
            return {"title": title, "outline": []}
        
        # Calculate document-wide font statistics
        font_sizes = [item["font_size"] for item in all_formatted_text]
        avg_font_size = sum(font_sizes) / len(font_sizes)
        max_font_size = max(font_sizes)
        
        logger.info(f"Font size stats - Avg: {avg_font_size:.2f}, Max: {max_font_size:.2f}")
        
        # Second pass: identify headings
        for item in all_formatted_text:
            text = item["text"].strip()
            font_size = item["font_size"]
            is_bold = self.is_bold(item["flags"])
            page = item["page"]
            
            # Skip very short or very long text
            if len(text) < 3 or len(text) > 200:
                continue
            
            # Check if it's a heading by formatting or pattern
            level = None
            
            # Check by font size and formatting
            if font_size > avg_font_size * 1.1:  # Larger than average
                level = self.determine_heading_level(text, font_size, is_bold, avg_font_size, max_font_size)
            
            # Check by pattern if not identified by formatting
            if not level and (is_bold or self.is_heading_by_pattern(text)):
                if font_size >= avg_font_size * 1.4:
                    level = "H1"
                elif font_size >= avg_font_size * 1.2:
                    level = "H2"
                elif is_bold or self.is_heading_by_pattern(text):
                    level = "H3"
            
            if level:
                # Clean up the heading text
                clean_text = re.sub(r'\s+', ' ', text).strip()
                outline.append({
                    "level": level,
                    "text": clean_text,
                    "page": page
                })
        
        # Remove duplicates and sort by page
        seen = set()
        unique_outline = []
        for item in outline:
            key = (item["level"], item["text"].lower(), item["page"])
            if key not in seen:
                seen.add(key)
                unique_outline.append(item)
        
        unique_outline.sort(key=lambda x: (x["page"], x["text"]))
        
        doc.close()
        
        logger.info(f"Extracted {len(unique_outline)} headings")
        return {
            "title": title,
            "outline": unique_outline
        }

def process_pdfs(input_dir: str, output_dir: str):
    """Process all PDFs in input directory and save results to output directory"""
    
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    # Create output directory if it doesn't exist
    output_path.mkdir(parents=True, exist_ok=True)
    
    extractor = PDFOutlineExtractor()
    
    # Find all PDF files
    pdf_files = list(input_path.glob("*.pdf"))
    
    if not pdf_files:
        logger.warning(f"No PDF files found in {input_dir}")
        return
    
    logger.info(f"Found {len(pdf_files)} PDF files to process")
    
    for pdf_file in pdf_files:
        try:
            logger.info(f"Processing: {pdf_file.name}")
            
            # Extract outline
            result = extractor.extract_outline(str(pdf_file))
            
            # Save result
            output_file = output_path / f"{pdf_file.stem}.json"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved result to: {output_file.name}")
            
        except Exception as e:
            logger.error(f"Error processing {pdf_file.name}: {str(e)}")
            
            # Create error output
            error_result = {"title": "Error", "outline": []}
            output_file = output_path / f"{pdf_file.stem}.json"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(error_result, f, indent=2)

def main():
    """Main entry point"""
    input_dir = "input"
    output_dir = "output"
    
    # For local testing, allow command line arguments
    if len(sys.argv) >= 3:
        input_dir = sys.argv[1]
        output_dir = sys.argv[2]
    
    logger.info(f"Input directory: {input_dir}")
    logger.info(f"Output directory: {output_dir}")
    
    if not os.path.exists(input_dir):
        logger.error(f"Input directory {input_dir} does not exist")
        sys.exit(1)
    
    process_pdfs(input_dir, output_dir)
    logger.info("Processing complete!")

if __name__ == "__main__":
    main()