# Citation Checker - User Guide

This guide provides practical instructions for using the Citation Checker tool to parse, validate, and check academic citations.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/citationchecker.git
   cd citationchecker
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Quick Start

### Using the Command Line Interface

The Citation Checker provides a command-line interface for parsing citations from files or direct text input.

#### Parse Citations from a File

```bash
python -m src.main -f path/to/your/paper.txt -o text
```

This will extract all citations from the file and display them in a readable text format.

#### Parse a Specific Citation

```bash
python -m src.main -t "Smith, J. (2020). The impact of AI on research. Journal of AI, 15(2), 45-67." -o text
```

This will parse the provided citation and display the structured result.

#### Output Formats

The tool supports multiple output formats:

- **Text** (default): Human-readable formatted text
  ```bash
  python -m src.main -f paper.txt -o text
  ```

- **JSON**: Structured JSON format for programmatic use
  ```bash
  python -m src.main -f paper.txt -o json
  ```

- **CSV**: Comma-separated values for spreadsheet import
  ```bash
  python -m src.main -f paper.txt -o csv
  ```

#### Save Output to a File

```bash
python -m src.main -f paper.txt -o json --output-file citations.json
```

This will save the parsed citations to the specified file instead of displaying them in the console.

### Using the Python API

You can also use the Citation Checker programmatically in your Python code.

#### Parse a Single Citation

```python
from src.parsers.apa_parser import APACitationParser

# Initialize the parser
parser = APACitationParser()

# Parse a citation
citation_text = "Smith, J. (2020). The impact of AI on research. Journal of AI, 15(2), 45-67."
citation = parser.parse(citation_text)

# Access citation components
print(f"Authors: {', '.join(citation.authors)}")
print(f"Year: {citation.year}")
print(f"Title: {citation.title}")
print(f"Source: {citation.source}")
print(f"DOI: {citation.doi}")
```

#### Extract Citations from Text

```python
from src.parsers.apa_parser import APACitationParser

# Initialize the parser
parser = APACitationParser()

# Load text from a file
with open("paper.txt", "r") as f:
    text = f.read()

# Extract all citations
citations = parser.extract_citations(text)

# Process the citations
for i, citation in enumerate(citations, 1):
    print(f"Citation {i}:")
    print(f"  Authors: {', '.join(citation.authors)}")
    print(f"  Title: {citation.title}")
    print(f"  Year: {citation.year}")
    print(f"  Confidence: {citation.confidence_score:.2f}")
    print()
```

## Common Use Cases

### 1. Checking References in a Research Paper

```bash
python -m src.main -f my_research_paper.txt -o text
```

This will extract all citations from your research paper and display them in a structured format, allowing you to verify that all citations are correctly formatted.

### 2. Converting Citations to Different Formats

```bash
# Extract citations to JSON for further processing
python -m src.main -f paper.txt -o json --output-file citations.json

# Extract citations to CSV for spreadsheet import
python -m src.main -f paper.txt -o csv --output-file citations.csv
```

### 3. Validating Individual Citations

```bash
python -m src.main -t "Smith, J. (2020). The impact of AI on research. Journal of AI, 15(2), 45-67." -o text
```

Use this to quickly check if a specific citation is correctly formatted and to see how the parser interprets it.

### 4. Batch Processing Multiple Files

You can use a simple shell script to process multiple files:

```bash
#!/bin/bash
for file in papers/*.txt; do
    filename=$(basename -- "$file")
    python -m src.main -f "$file" -o json --output-file "results/${filename%.txt}.json"
done
```

## Understanding the Output

### Citation Components

Each parsed citation includes:

- **Authors**: List of author names
- **Year**: Publication year
- **Title**: Title of the work
- **Source**: Journal, book, or other source
- **Volume/Issue**: For journal articles
- **Pages**: Page range
- **DOI/URL**: Digital identifiers
- **Confidence Score**: How confident the parser is in the result (0-1)

### Confidence Scores

The confidence score indicates how reliable the parsing result is:

- **0.9-1.0**: High confidence, all essential components found
- **0.7-0.9**: Good confidence, most components found
- **0.5-0.7**: Medium confidence, some components may be missing
- **< 0.5**: Low confidence, parsing may be incomplete or incorrect

## Troubleshooting

### Citation Not Detected

If your citations aren't being detected:

1. Check that they follow standard APA format
2. Ensure there's proper spacing between citations
3. Try providing the citation directly using the `-t` option to see if it can be parsed individually

### Incorrect Author Parsing

If authors are parsed incorrectly:

1. Ensure proper comma and ampersand usage in the original citation
2. Check for consistent spacing between author names
3. Verify that initials have periods

### Low Confidence Scores

If you're getting low confidence scores:

1. Check that all essential components are present (authors, year, title, source)
2. Ensure proper punctuation between citation components
3. Add missing metadata like DOI, volume, issue, or pages if available

## Demo Script

The project includes a demo script that shows basic usage:

```bash
python demo_parser.py
```

This will demonstrate:
1. Parsing a single citation
2. Extracting citations from a text with multiple citations

## Advanced Usage

### Custom Parsing Logic

You can extend the base parser to create custom parsing logic for specific citation formats:

```python
from src.parsers.base_parser import BaseCitationParser
from src.models.citation import Citation

class MyCustomParser(BaseCitationParser):
    def __init__(self):
        super().__init__()
        self.format_name = "custom"
        
    def parse(self, text):
        # Your custom parsing logic here
        # ...
        return citation
        
    def extract_citations(self, text):
        # Your custom extraction logic here
        # ...
        return citations
```

### Integration with Other Tools

The JSON output format makes it easy to integrate with other tools:

```bash
# Extract citations to JSON
python -m src.main -f paper.txt -o json --output-file citations.json

# Use jq to filter or transform the JSON
cat citations.json | jq '.citations[] | select(.year > 2010)'
```

## Limitations

- Currently only supports APA citation format
- May have difficulty with highly non-standard citation formats
- Does not verify citation accuracy against external databases
