# Adobe India Hackathon - Round 1A: PDF Outline Extractor

## Overview

This solution extracts structured outlines from PDF documents, including:
- Document title
- Heading hierarchy (H1, H2, H3) with page numbers
- Output in required JSON format

## Approach

### 1. PDF Text Extraction
- Uses PyMuPDF (fitz) for efficient PDF processing
- Extracts text with formatting information (font size, style, position)
- Processes all pages to gather document-wide statistics

### 2. Title Extraction
- First attempts to extract from PDF metadata
- Falls back to analyzing first few pages for title candidates
- Uses font size, positioning, and formatting cues
- Scores candidates based on multiple criteria

### 3. Heading Detection
- **Multi-modal approach** combining:
  - **Font Analysis**: Compares font sizes against document averages
  - **Pattern Matching**: Identifies common heading patterns (numbered sections, chapters, etc.)
  - **Formatting Cues**: Bold text, capitalization patterns
  - **Structural Analysis**: Position and context within document

### 4. Heading Level Classification
- **H1**: Largest fonts (≥1.8x average) or pattern-based major sections
- **H2**: Medium fonts (≥1.4x average) or secondary section indicators  
- **H3**: Smaller but emphasized text (≥1.2x average, bold, or pattern-matched)

### 5. Output Processing
- Removes duplicates and false positives
- Sorts by page number for logical flow
- Outputs clean JSON in required format

## Models and Libraries Used

- **PyMuPDF (1.23.26)**: Primary PDF processing library
  - Lightweight (~15MB including dependencies)
  - Fast text extraction with formatting
  - No ML models - rule-based approach
- **Standard Python libraries**: re, json, pathlib, logging

## Key Features

- **No ML Dependencies**: Uses efficient rule-based algorithms
- **Multilingual Support**: Handles Unicode text properly
- **Robust Pattern Recognition**: Multiple heading detection strategies
- **Performance Optimized**: Processes 50-page PDFs in ~2-5 seconds
- **Offline Operation**: No network calls required

## Architecture

```
Input PDF → Text Extraction → Font Analysis → Pattern Matching → Level Classification → JSON Output
```

## Building and Running

### Build Docker Image
```bash
docker build --platform linux/amd64 -t pdf-outline-extractor:v1.0 .
```

### Run Container
```bash
docker run --rm -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output --network none pdf-outline-extractor:v1.0
```

### Local Development
```bash
pip install -r requirements.txt
python pdf_outline_extractor.py input_dir output_dir
```

## Input/Output Format

### Expected Input
- PDF files in `/app/input/` directory
- Up to 50 pages per PDF

### Output Format
```json
{
  "title": "Document Title",
  "outline": [
    { "level": "H1", "text": "Introduction", "page": 1 },
    { "level": "H2", "text": "Overview", "page": 2 },
    { "level": "H3", "text": "Key Concepts", "page": 3 }
  ]
}
```

## Performance Characteristics

- **Processing Time**: ~2-5 seconds per 50-page PDF
- **Memory Usage**: <100MB peak
- **Model Size**: 0MB (no ML models)
- **Dependencies**: <20MB total

## Error Handling

- Graceful handling of corrupted PDFs
- Fallback mechanisms for title extraction
- Robust text processing for various PDF formats
- Logging for debugging and monitoring

## Testing Strategy

- Tested across various PDF types (academic papers, reports, books)
- Handles different font schemes and layouts
- Validates against common heading patterns
- Stress tested with complex multi-column documents

## Limitations and Considerations

- Best performance on well-structured documents
- May require adjustment for highly non-standard formats
- Title extraction depends on document quality and metadata
- Complex multi-column layouts may need additional tuning