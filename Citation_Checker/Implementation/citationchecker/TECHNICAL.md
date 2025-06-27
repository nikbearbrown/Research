# Citation Checker - Technical Documentation

This document provides technical details about the implementation of the Citation Checker project, focusing on the algorithms, techniques, and design decisions.

## Parser Implementation Details

### Regex Patterns

The APA parser uses several regex patterns to identify and extract citation components:

```python
# Author(s), year pattern - matches "Author, A. A., & Author, B. B. (Year)"
"author_year": r"([^(]+)\s*\((\d{4}[a-z]?)\)"

# Title pattern - matches the title after the year and period
"title": r"\(\d{4}[a-z]?\)\.\s+([^.]+)"

# Journal/source pattern - matches journal name and potentially volume/issue
"journal": r"([A-Z][^,]+)(?:,\s*(\d+)(?:\((\d+[A-Za-z]?)\))?)?",

# Pages pattern - matches page ranges in various formats
"pages": r"(\d+)[-–](\d+)"

# DOI pattern - matches DOI in various formats
"doi": r"https?://doi\.org/(.+)$|DOI:\s*(.+)$|10\.\d{4,}/[-._;()/:A-Za-z0-9]+"

# URL pattern - matches URLs in various formats
"url": r"Retrieved from\s+(.+)$|Available at\s+(.+)$|https?://[^\s)\"]+",
```

### Complete Citation Pattern

For matching complete APA citations, a comprehensive regex pattern is used:

```python
r"([^(]+)\s*\((\d{4}[a-z]?)\)\.\s+([^.]+)\.\s+([^,]+)(?:,\s*(\d+)(?:\((\d+[A-Za-z]?)\))?)?,?\s*(?:(\d+[-–]\d+))?\.\s*(?:https?://doi\.org/(.+)|DOI:\s*(.+))?"
```

This pattern captures:
1. Author string
2. Year (with optional letter suffix)
3. Title
4. Source/journal
5. Volume (optional)
6. Issue (optional)
7. Pages (optional)
8. DOI (optional, in two possible formats)

### Citation Extraction Algorithm

The citation extraction process follows these steps:

1. **Identify Reference Section**: Look for headings like "References", "Bibliography", or "Works Cited"
   ```python
   references_match = re.search(r'(?:References|Bibliography|Works Cited)[:.\n]+(.*)', text, re.IGNORECASE | re.DOTALL)
   ```

2. **Split Text into Potential Citations**:
   - If a references section is found, split by newlines or newlines followed by capital letters
   - Otherwise, split the full text by periods followed by multiple spaces, newlines, or newlines followed by capital letters
   ```python
   potential_citations = re.split(r'\n\s*\n|\n(?=[A-Z])', references_text)
   # or
   potential_citations = re.split(r'\.\s{2,}|\.\n+|\n(?=[A-Z])', text)
   ```

3. **Filter Potential Citations**:
   - Skip very short strings (< 20 characters)
   - Look for author-year pattern (text followed by year in parentheses)
   ```python
   if len(potential.strip()) < 20:
       continue
   if re.search(r'[A-Za-z]+.*\(\d{4}[a-z]?\)', potential):
       # Process as potential citation
   ```

4. **Parse Each Potential Citation**:
   - Try to match the complete citation pattern
   - If that fails, fall back to extracting components individually
   - Filter out citations with low confidence scores (< 0.5)

### Author Parsing Algorithm

The author parsing algorithm is particularly complex due to the various formats authors can be listed in:

1. **Split by '&'** to separate the last author from the rest:
   ```python
   if '&' in authors_str:
       parts = authors_str.split('&')
       main_authors = parts[0].strip()
       last_author = parts[1].strip()
   ```

2. **Process Main Authors**:
   - Split by commas
   - Process pairs of lastname and initials
   - Handle cases where initials are separated from lastname

3. **Process Last Author**:
   - Handle comma-separated lastname and initials
   - Add to the author list

4. **Filter and Normalize**:
   - Remove empty strings
   - Normalize each author name to a standard format
   ```python
   return [normalize_author_name(author) for author in authors if author.strip()]
   ```

### Confidence Score Calculation

The confidence score is calculated based on the presence and completeness of citation components:

```python
score = 0.0

# Check essential components
if citation.authors and len(citation.authors) > 0:
    score += 0.3
if citation.year:
    score += 0.1
if citation.title:
    score += 0.3
if citation.source:
    score += 0.2

# Additional points for metadata
if citation.doi or citation.url:
    score += 0.05
if citation.volume or citation.issue:
    score += 0.05

return min(score, 1.0)
```

## Design Patterns

### Factory Method Pattern

The project uses a simple factory method pattern in the main module to create parser instances:

```python
def get_parser(parser_name: str):
    """Get a parser instance by name."""
    if parser_name.lower() == "apa":
        return APACitationParser()
    # Add more parsers here as they are implemented
    return None
```

### Template Method Pattern

The `BaseCitationParser` abstract class defines a template method pattern:

- Abstract methods (`parse`, `extract_citations`) that subclasses must implement
- Concrete methods (`calculate_confidence`) that provide default behavior but can be overridden

### Data Transfer Object (DTO)

The `Citation` class acts as a DTO, providing a standardized structure for transferring citation data between components:

```python
@dataclass
class Citation:
    # Basic citation components
    authors: List[str]
    year: Optional[int]
    title: str
    source: str
    
    # Additional metadata
    doi: Optional[str] = None
    url: Optional[str] = None
    # ...
```

## Performance Considerations

### Regex Compilation

Regex patterns are compiled once during parser initialization to improve performance:

```python
self.apa_pattern = re.compile(
    r"([^(]+)\s*\((\d{4}[a-z]?)\)\.\s+([^.]+)\.\s+([^,]+)(?:,\s*(\d+)(?:\((\d+[A-Za-z]?)\))?)?,?\s*(?:(\d+[-–]\d+))?\.\s*(?:https?://doi\.org/(.+)|DOI:\s*(.+))?",
    re.DOTALL
)
```

### Fallback Parsing

The parser uses a two-tiered approach:
1. Try to match the complete pattern first (faster, more accurate)
2. Fall back to extracting components individually if the complete pattern fails (slower, less accurate)

This balances performance with robustness.

### Early Filtering

The citation extraction process filters out unlikely candidates early:
- Skipping very short strings
- Checking for basic patterns before attempting full parsing
- Using confidence scores to filter out low-quality matches

## Error Handling

The parser is designed to be robust against various citation formats and errors:

- Returns `None` for unparseable citations
- Uses confidence scores to indicate parsing quality
- Provides fallback parsing for non-standard formats
- Handles missing components gracefully

## Extensibility

The project is designed for easy extension:

1. **New Citation Formats**: Create a new parser class that inherits from `BaseCitationParser`
2. **New Output Formats**: Add to the `format_citation_output` function in `main.py`
3. **New Citation Types**: Extend the `_determine_citation_type` method in the parser classes

## Testing Strategy

The test suite follows these principles:

1. **Parameterized Tests**: Using pytest's parameterization to test multiple citation formats
2. **Test Data Separation**: Keeping test data in separate JSON files for maintainability
3. **Component Testing**: Testing individual components (parsing, extraction, confidence calculation)
4. **Edge Case Testing**: Specifically testing edge cases and error conditions

## Future Technical Improvements

1. **Performance Optimization**:
   - Caching frequently used regex patterns
   - Optimizing the citation extraction algorithm for large texts

2. **Machine Learning Integration**:
   - Using ML models to improve parsing accuracy
   - Training on large citation datasets

3. **Parallel Processing**:
   - Processing multiple citations in parallel for large documents

4. **Database Integration**:
   - Connecting to citation databases for validation
   - Storing parsed citations for future reference
