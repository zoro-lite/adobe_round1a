#!/usr/bin/env python3
"""
Test script for PDF Outline Extractor
"""

import json
import os
from pdf_outline_extractor import PDFOutlineExtractor

def test_extractor():
    """Test the PDF outline extractor with a sample"""
    
    # Create test directories
    os.makedirs("test_input", exist_ok=True)
    os.makedirs("test_output", exist_ok=True)
    
    extractor = PDFOutlineExtractor()
    
    print("PDF Outline Extractor Test")
    print("=" * 40)
    
    # Check if test PDF exists
    test_files = [f for f in os.listdir("test_input") if f.endswith('.pdf')]
    
    if not test_files:
        print("No PDF files found in test_input directory.")
        print("Please add some PDF files to test_input/ to test the extractor.")
        return
    
    for pdf_file in test_files:
        print(f"\nProcessing: {pdf_file}")
        pdf_path = os.path.join("test_input", pdf_file)
        
        try:
            result = extractor.extract_outline(pdf_path)
            
            print(f"Title: {result['title']}")
            print(f"Headings found: {len(result['outline'])}")
            
            for i, heading in enumerate(result['outline'][:10]):  # Show first 10
                print(f"  {i+1}. {heading['level']} - {heading['text']} (Page {heading['page']})")
            
            if len(result['outline']) > 10:
                print(f"  ... and {len(result['outline']) - 10} more headings")
            
            # Save result
            output_file = os.path.join("test_output", f"{os.path.splitext(pdf_file)[0]}.json")
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            print(f"Result saved to: {output_file}")
            
        except Exception as e:
            print(f"Error processing {pdf_file}: {str(e)}")

if __name__ == "__main__":
    test_extractor()