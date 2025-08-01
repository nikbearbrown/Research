import re
from typing import List, Optional, Tuple
from src.models.citation import Citation
from src.parsers.base_parser import BaseCitationParser
from src.parsers.utils import (
    normalize_author_name, 
    extract_urls, 
    extract_year, 
    extract_doi,
    clean_title,
    extract_pages
)

class MLACitationParser(BaseCitationParser):
    """Parser for MLA citation format.
    
    This parser implements the specific rules and patterns for MLA-style citations,
    which typically follow the format:
    Author, First. "Title." Source, vol. X, no. Y, Date, pp. X-Y.
    """
    
    def __init__(self):
        super().__init__()
        self.format_name = "mla"
        
        # Regex patterns for MLA citation components
        self.patterns = {
            # Author pattern - matches "Last, First" or "Last, First, and Second Author" or "Last, First, et al."
            "author": r"^([^.]+?)(?:\.|,\s+(?:and\s+|et\s+al\.))(?:\s|$)",
            
            # Multiple authors with "and" - "Smith, John, and Mary Johnson"
            "authors_and": r"^(.+?),\s+and\s+(.+?)\.",
            
            # Multiple authors with "et al." - "Smith, John, et al."
            "authors_et_al": r"^(.+?),\s+et\s+al\.",
            
            # Title pattern - matches quoted title "Title of Work"
            "title": r'"([^"]+)"',
            
            # Source/container pattern - matches source after title
            "source": r'"[^"]+"\.\s*([^,]+)',
            
            # Volume pattern - "vol. 15"
            "volume": r'vol\.\s*(\d+)',
            
            # Issue pattern - "no. 2"
            "issue": r'no\.\s*(\d+[A-Za-z]?)',
            
            # Pages pattern - "pp. 45-67" or "p. 45"
            "pages_mla": r'pp?\.\s*(\d+(?:[-–]\d+)?)',
            
            # Date patterns - various MLA date formats
            "date_year": r'\b(19|20)\d{2}\b',
            "date_full": r'\b\d{1,2}\s+[A-Za-z]{3,9}\.?\s+(19|20)\d{2}\b',
            
            # Web citation pattern - for URLs and access dates
            "web_url": r'(https?://[^\s,]+)',
            "access_date": r'Accessed\s+(\d{1,2}\s+[A-Za-z]{3,9}\.?\s+\d{4})',
            
            # Publisher pattern
            "publisher": r'([A-Z][^,]+),\s+(19|20)\d{2}',
        }
        
        # Complete MLA patterns for different citation types
        self.mla_patterns = {
            # Journal article: Author. "Title." Journal, vol. X, no. Y, Date, pp. X-Y.
            "journal": re.compile(
                r'^(.+?)\.\s*"([^"]+)"\.\s*([^,]+),\s*(?:vol\.\s*(\d+),?\s*)?(?:no\.\s*(\d+[A-Za-z]?),?\s*)?(.+?),\s*pp?\.\s*(\d+(?:[-–]\d+)?)\.',
                re.DOTALL
            ),
            
            # Book: Author. Title. Publisher, Year.
            "book": re.compile(
                r'^(.+?)\.\s*([^.]+)\.\s*([^,]+),\s*(\d{4})\.',
                re.DOTALL
            ),
            
            # Web article: Author. "Title." Website, Date, URL.
            "web": re.compile(
                r'^(.+?)\.\s*"([^"]+)"\.\s*([^,]+),\s*(.+?),\s*(https?://[^\s,]+)',
                re.DOTALL
            ),
            
            # Book chapter: Author. "Chapter Title." Book Title, edited by Editor, Publisher, Year, pp. X-Y.
            "chapter": re.compile(
                r'^(.+?)\.\s*"([^"]+)"\.\s*([^,]+),\s*edited by\s+(.+?),\s*([^,]+),\s*(\d{4}),\s*pp?\.\s*(\d+(?:[-–]\d+)?)\.',
                re.DOTALL
            ),
        }
    
    def parse(self, text: str) -> Optional[Citation]:
        """Parse a single MLA citation string.
        
        Args:
            text: A string containing a single MLA citation
            
        Returns:
            Citation object if parsing successful, None otherwise
        """
        text = text.strip()
        
        # Try each MLA pattern type
        for citation_type, pattern in self.mla_patterns.items():
            match = pattern.match(text)
            if match:
                return self._parse_by_type(text, citation_type, match)
        
        # Fallback: try to extract components individually
        return self._fallback_parse(text)
    
    def _parse_by_type(self, text: str, citation_type: str, match) -> Optional[Citation]:
        """Parse citation based on identified type and regex match."""
        
        if citation_type == "journal":
            authors_str, title, source, volume, issue, date_part, pages = match.groups()
            
            authors = self._process_authors(authors_str)
            year = self._extract_year_from_text(date_part)
            
            citation = Citation(
                authors=authors,
                year=year,
                title=clean_title(title),
                source=source.strip(),
                volume=volume,
                issue=issue,
                pages=pages,
                citation_type="article",
                citation_format="mla",
                citation_text=text
            )
            
        elif citation_type == "book":
            authors_str, title, publisher, year_str = match.groups()
            
            authors = self._process_authors(authors_str)
            year = int(year_str) if year_str else None
            
            citation = Citation(
                authors=authors,
                year=year,
                title=clean_title(title),
                source=title.strip(),  # For books, source is the book title
                publisher=publisher.strip(),
                citation_type="book",
                citation_format="mla",
                citation_text=text
            )
            
        elif citation_type == "web":
            authors_str, title, website, date_part, url = match.groups()
            
            authors = self._process_authors(authors_str)
            year = self._extract_year_from_text(date_part)
            
            citation = Citation(
                authors=authors,
                year=year,
                title=clean_title(title),
                source=website.strip(),
                url=url.strip(),
                citation_type="web",
                citation_format="mla",
                citation_text=text
            )
            
        elif citation_type == "chapter":
            authors_str, chapter_title, book_title, editor, publisher, year_str, pages = match.groups()
            
            authors = self._process_authors(authors_str)
            year = int(year_str) if year_str else None
            
            citation = Citation(
                authors=authors,
                year=year,
                title=clean_title(chapter_title),
                source=book_title.strip(),
                publisher=publisher.strip(),
                pages=pages,
                citation_type="book_chapter",
                citation_format="mla",
                citation_text=text
            )
        
        else:
            return None
        
        # Extract additional metadata
        citation.doi = extract_doi(text)
        if not citation.url:
            urls = extract_urls(text)
            if urls:
                citation.url = urls[0]
        
        # Calculate confidence
        citation.confidence_score = self.calculate_confidence(citation)
        
        return citation
    
    def _fallback_parse(self, text: str) -> Optional[Citation]:
        """Fallback method for when the main regex patterns don't match."""
        authors = self._extract_authors(text)
        title = self._extract_title(text)
        source = self._extract_source(text)
        year = self._extract_year_from_text(text)
        
        if authors and title and source:
            citation = Citation(
                authors=authors,
                year=year,
                title=title,
                source=source,
                citation_format="mla",
                citation_text=text
            )
            
            # Extract additional metadata
            citation.doi = extract_doi(text)
            citation.url = self._extract_url(text)
            citation.pages = self._extract_pages_mla(text)
            citation.volume = self._extract_volume(text)
            citation.issue = self._extract_issue(text)
            citation.citation_type = self._determine_citation_type(text)
            
            # Calculate confidence (will be lower for partial matches)
            citation.confidence_score = self.calculate_confidence(citation)
            
            return citation
        
        return None
    
    def extract_citations(self, text: str) -> List[Citation]:
        """Extract all MLA citations from a larger text.
        
        Args:
            text: A string that may contain multiple MLA citations
            
        Returns:
            List of Citation objects found in the text
        """
        citations = []
        
        # Look for a works cited section
        works_cited_match = re.search(r'(?:Works Cited|Bibliography|References)[:.\n]+(.*)', text, re.IGNORECASE | re.DOTALL)
        if works_cited_match:
            # If we found a works cited section, focus on that
            works_cited_text = works_cited_match.group(1)
            # Split by newlines (common format for works cited lists)
            potential_citations = re.split(r'\n\s*\n|\n(?=[A-Z])', works_cited_text)
        else:
            # Otherwise, try to find citations in the full text
            # Split by periods followed by multiple spaces or newlines, or by newlines followed by capital letters
            potential_citations = re.split(r'\.\s{2,}|\.\n+|\n(?=[A-Z])', text)
        
        for potential in potential_citations:
            # Skip very short strings
            if len(potential.strip()) < 20:
                continue
                
            # Basic check: does it look like it might be an MLA citation?
            # Look for author pattern followed by title in quotes or just title in quotes
            if (re.search(r'[A-Za-z]+.*"[^"]+"', potential) or 
                re.search(r'^[A-Z][a-z]+,\s+[A-Z][a-z]+', potential)):
                citation = self.parse(potential)
                if citation and citation.confidence_score > 0.5:
                    citations.append(citation)
        
        return citations
    
    def _process_authors(self, authors_str: str) -> List[str]:
        """Process author string into list of normalized author names for MLA format."""
        authors_str = authors_str.strip()
        
        # Handle "et al." case
        et_al_match = re.match(self.patterns["authors_et_al"], authors_str)
        if et_al_match:
            first_author = et_al_match.group(1).strip()
            # Remove any trailing comma from the first author
            if first_author.endswith(','):
                first_author = first_author[:-1].strip()
            return [normalize_author_name(first_author)]
        
        # Handle "and" case - "Smith, John, and Mary Johnson"
        and_match = re.match(self.patterns["authors_and"], authors_str)
        if and_match:
            first_author = and_match.group(1).strip()
            second_author = and_match.group(2).strip()
            return [normalize_author_name(first_author), normalize_author_name(second_author)]
        
        # Handle multiple authors separated by commas (more than 2)
        if ', and ' in authors_str:
            # Split at ", and " to get the last author
            parts = authors_str.split(', and ')
            if len(parts) == 2:
                # Process all authors before "and"
                main_authors = parts[0].split(', ')
                last_author = parts[1]
                
                authors = []
                # Process main authors (pairs of lastname, firstname)
                current_author = ""
                for i, part in enumerate(main_authors):
                    if i % 2 == 0:  # Even index = lastname
                        current_author = part.strip()
                    else:  # Odd index = firstname
                        if current_author:
                            authors.append(f"{current_author}, {part.strip()}")
                            current_author = ""
                
                # Add any remaining single author
                if current_author:
                    authors.append(current_author)
                
                # Add the last author
                authors.append(last_author.strip())
                
                return [normalize_author_name(author) for author in authors if author.strip()]
        
        # Single author case - "Smith, John"
        if ',' in authors_str:
            return [normalize_author_name(authors_str)]
        
        # Fallback - just return as is
        return [normalize_author_name(authors_str)]
    
    def _extract_authors(self, text: str) -> List[str]:
        """Extract authors from citation text."""
        # Look for author pattern at the beginning
        author_match = re.match(r'^([^.]+?)\.', text)
        if author_match:
            authors_str = author_match.group(1)
            return self._process_authors(authors_str)
        return []
    
    def _extract_title(self, text: str) -> str:
        """Extract title from citation text."""
        # Look for quoted title
        title_match = re.search(self.patterns["title"], text)
        if title_match:
            return clean_title(title_match.group(1))
        
        # Fallback: look for title after author and before source
        parts = text.split('. ')
        if len(parts) >= 2:
            # Remove quotes if present
            title = parts[1].strip()
            if title.startswith('"') and title.endswith('"'):
                title = title[1:-1]
            return clean_title(title)
        
        return ""
    
    def _extract_source(self, text: str) -> str:
        """Extract source from citation text."""
        # Look for source after title
        source_match = re.search(self.patterns["source"], text)
        if source_match:
            return source_match.group(1).strip()
        
        # Fallback: look for source in the middle of citation
        parts = text.split('. ')
        if len(parts) >= 3:
            source_part = parts[2].split(',')[0]
            return source_part.strip()
        
        return ""
    
    def _extract_year_from_text(self, text: str) -> Optional[int]:
        """Extract year from text, handling various MLA date formats."""
        if not text:
            return None
        
        # Try full date format first (e.g., "15 Mar. 2020")
        full_date_match = re.search(self.patterns["date_full"], text)
        if full_date_match:
            year_part = full_date_match.group(0)
            year_match = re.search(r'(\d{4})', year_part)
            if year_match:
                return int(year_match.group(1))
        
        # Try simple year format
        year_match = re.search(self.patterns["date_year"], text)
        if year_match:
            return int(year_match.group(0))
        
        return None
    
    def _extract_url(self, text: str) -> Optional[str]:
        """Extract URL from citation text."""
        urls = extract_urls(text)
        if urls:
            return urls[0]
        
        # Also check for MLA web pattern
        web_match = re.search(self.patterns["web_url"], text)
        if web_match:
            return web_match.group(1)
        
        return None
    
    def _extract_pages_mla(self, text: str) -> Optional[str]:
        """Extract page numbers in MLA format."""
        pages_match = re.search(self.patterns["pages_mla"], text)
        if pages_match:
            return pages_match.group(1)
        
        # Fallback to general page extraction
        return extract_pages(text)
    
    def _extract_volume(self, text: str) -> Optional[str]:
        """Extract volume number in MLA format."""
        volume_match = re.search(self.patterns["volume"], text)
        if volume_match:
            return volume_match.group(1)
        return None
    
    def _extract_issue(self, text: str) -> Optional[str]:
        """Extract issue number in MLA format."""
        issue_match = re.search(self.patterns["issue"], text)
        if issue_match:
            return issue_match.group(1)
        return None
    
    def _determine_citation_type(self, text: str) -> str:
        """Determine the type of citation (article, book, chapter, etc.)."""
        # Look for indicators of citation type
        if re.search(r'"[^"]+".*[A-Z][^,]+,\s*vol\.|journal|magazine', text.lower()):
            return "article"
        if re.search(r'edited by|chapter', text.lower()):
            return "book_chapter"
        if re.search(r'https?://|web|website|accessed', text.lower()):
            return "web"
        if re.search(r'[A-Z][^.]+\.\s*[A-Z][^.]+\.\s*[A-Z][^,]+,\s*\d{4}', text):
            return "book"
        if re.search(r'conference|proceedings|symposium', text.lower()):
            return "conference"
        if re.search(r'thesis|dissertation', text.lower()):
            return "thesis"
        
        # Default to article as most common type
        return "article"
    
    def calculate_confidence(self, citation: Citation) -> float:
        """Calculate confidence score for a parsed MLA citation.
        
        Args:
            citation: A Citation object to evaluate
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        score = 0.0
        
        # Check essential components
        if citation.authors and len(citation.authors) > 0:
            score += 0.3
        if citation.title:
            score += 0.3
        if citation.source:
            score += 0.2
        if citation.year:
            score += 0.1
        
        # Additional points for metadata
        if citation.doi or citation.url:
            score += 0.05
        if citation.volume or citation.issue:
            score += 0.05
        
        return min(score, 1.0)
