# Citation Checker

A Python library for parsing academic citations and verifying source availability.

## Current Status: 35-40% Complete

**✅ Implemented:**
- APA and MLA citation parsing
- Web crawling for 13+ academic domains (arXiv, PubMed, IEEE, etc.)
- Source availability verification
- Command-line interface
- Comprehensive test suite

**❌ In Development:**
- Chicago citation format
- Content verification (quoted text matching)
- Web dashboard
- Detailed reporting system

## Quick Start

### Installation
```bash
pip install -r requirements.txt
```

### Basic Usage

**Parse Citations:**
```python
from src.parsers.apa_parser import APACitationParser
from src.parsers.mla_parser import MLACitationParser

# APA format
apa_parser = APACitationParser()
citation = apa_parser.parse("Smith, J. (2020). Title. Journal, 15(2), 45-67.")

# MLA format
mla_parser = MLACitationParser()
citation = mla_parser.parse('Smith, John. "Title." Journal, vol. 15, no. 2, 2020, pp. 45-67.')
```

**Verify Sources:**
```python
from src.crawlers.crawler_manager import CrawlerManager

with CrawlerManager() as manager:
    result = manager.crawl_url("https://arxiv.org/abs/2101.00001")
    print(f"Source available: {result.success}")
```

**Command Line:**
```bash
# Parse citations from file
python -m src.main -f paper.txt -o json

# Parse single citation
python -m src.main -t "Smith, J. (2020). Title. Journal, 15(2), 45-67."
```

## Features

### Citation Parsing
- **APA Format**: Full support with confidence scoring
- **MLA Format**: 9th edition support with various citation types
- **Author Processing**: Handles multiple authors, "et al.", etc.
- **Metadata Extraction**: DOI, URL, volume, pages, etc.

### Web Crawling
- **Academic Sources**: arXiv, PubMed, IEEE Xplore, ACM, Nature, Science, PLOS, ScienceDirect, Springer, JSTOR, Google Scholar
- **General Web**: Intelligent content extraction from any website
- **Concurrent Processing**: Multi-threaded crawling
- **Rate Limiting**: Respectful crawling with robots.txt compliance

### Testing
```bash
python -m pytest  # Run all tests
python demo_parser.py  # Citation parsing demo
python demo_crawler.py  # Web crawling demo
```

## Project Structure
```
src/
├── parsers/          # Citation parsers (APA, MLA)
├── crawlers/         # Web crawling system
├── models/           # Data models
├── tests/            # Test suite
└── main.py           # CLI interface
```

## Roadmap

**Next Phase (Weeks 4-5):**
- Content verification engine
- Text similarity analysis
- Enhanced reporting system

**Future:**
- Chicago citation format
- Web dashboard
- Educational components
- API endpoints

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

## License

MIT License - see [LICENSE](LICENSE) file.
