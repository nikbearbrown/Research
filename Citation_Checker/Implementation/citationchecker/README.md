# Citation Checker

A Python library for parsing, validating, and checking academic citations.

## Project Overview

The Citation Checker project is designed to parse and validate academic citations from various formats (currently focusing on APA style). It provides tools to extract citations from text, parse them into structured data, and validate their components.

## Project Structure

```
citationchecker/
├── demo_parser.py              # Demo script showing basic usage
├── requirements.txt            # Project dependencies
└── src/                        # Main source code
    ├── __init__.py
    ├── main.py                 # Command-line interface
    ├── models/                 # Data models
    │   ├── __init__.py
    │   └── citation.py         # Citation data model
    ├── parsers/                # Citation parsers
    │   ├── __init__.py
    │   ├── apa_parser.py       # APA citation format parser
    │   ├── base_parser.py      # Abstract base parser class
    │   └── utils.py            # Utility functions for parsing
    └── tests/                  # Test suite
        ├── __init__.py
        ├── test_apa_parser.py  # Tests for APA parser
        ├── test_simple.py      # Simple tests
        └── test_data/          # Test data
            └── apa_citations.json  # Sample APA citations for testing
```

## Components

### 1. Citation Model (`src/models/citation.py`)

The `Citation` class provides a standardized data structure for representing citations across different formats. It includes:

- **Basic Components**: authors, year, title, source
- **Additional Metadata**: DOI, URL, volume, issue, pages, publisher
- **Citation Metadata**: type, format, original text, confidence score

### 2. Parser Architecture

#### Base Parser (`src/parsers/base_parser.py`)

The `BaseCitationParser` is an abstract base class that defines the interface for all citation parsers:

- `parse(text)`: Parse a single citation string
- `extract_citations(text)`: Extract all citations from a larger text
- `calculate_confidence(citation)`: Calculate confidence score for a parsed citation

#### APA Parser (`src/parsers/apa_parser.py`)

The `APACitationParser` implements parsing for APA citation format:

- Uses regex patterns to identify and extract citation components
- Handles various APA citation formats and variations
- Provides fallback parsing for non-standard formats
- Calculates confidence scores based on completeness

#### Utility Functions (`src/parsers/utils.py`)

Helper functions for parsing citations:

- `normalize_author_name`: Standardize author name formats
- `extract_urls`, `extract_year`, `extract_doi`: Extract specific components
- `clean_title`: Remove unnecessary punctuation from titles
- `extract_pages`, `extract_volume_issue`: Extract publication details

### 3. Command-line Interface (`src/main.py`)

Provides command-line functionality:

- Parse citations from files or text input
- Select parser type (currently only APA)
- Output in various formats (text, JSON, CSV)
- Save results to file or display in console

### 4. Demo Script (`demo_parser.py`)

Demonstrates basic usage of the citation parser:

- Parsing a single citation
- Extracting citations from text with multiple citations

## How It Works

### Citation Parsing Process

1. **Input**: The system takes text containing one or more citations.

2. **Extraction**: For text with multiple citations, the `extract_citations` method:
   - Looks for a references section
   - Splits text into potential citation chunks
   - Filters chunks based on length and basic patterns

3. **Parsing**: For each potential citation, the `parse` method:
   - Attempts to match the complete citation pattern
   - If successful, extracts all components (authors, year, title, etc.)
   - If not, falls back to extracting components individually

4. **Author Processing**: The `_process_authors` method:
   - Handles APA-style author lists with "&" separators
   - Correctly pairs lastnames with initials
   - Normalizes author name formats

5. **Metadata Extraction**: Additional methods extract:
   - DOI and URL information
   - Volume and issue numbers
   - Page ranges
   - Citation type (article, book, etc.)

6. **Confidence Calculation**: The system calculates a confidence score (0-1) based on:
   - Presence of required fields (authors, title, source)
   - Presence of additional metadata (year, DOI, volume, etc.)

7. **Output**: Returns structured `Citation` objects with all extracted data

### Example Usage

#### Command Line

```bash
# Parse citations from a file
python -m src.main -f path/to/paper.txt -o json

# Parse a specific citation
python -m src.main -t "Smith, J. (2020). Title. Journal, 15(2), 45-67." -o text
```

#### Python API

```python
from src.parsers.apa_parser import APACitationParser

# Initialize parser
parser = APACitationParser()

# Parse a single citation
citation = parser.parse("Smith, J. (2020). Title. Journal, 15(2), 45-67.")

# Extract citations from text
citations = parser.extract_citations(text_with_multiple_citations)
```

## Testing

The project includes a comprehensive test suite:

- `test_apa_parser.py`: Tests for the APA citation parser
- `test_data/apa_citations.json`: Sample citations for testing

Run tests with pytest:

```bash
python -m pytest
```

## Future Development

Potential areas for expansion:

1. Support for additional citation formats (MLA, Chicago, IEEE, etc.)
2. Integration with reference databases for validation
3. Citation correction suggestions
4. Web interface for citation checking
5. Batch processing capabilities
