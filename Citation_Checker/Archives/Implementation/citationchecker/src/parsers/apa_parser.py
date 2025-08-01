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
    extract_pages,
    extract_volume_issue
)

class APACitationParser(BaseCitationParser):
    """Parser for APA citation format.
    
    This parser implements the specific rules and patterns for APA-style citations,
    which typically follow the format:
    Author, A. A., & Author, B. B. (Year). Title of the article. Journal Name, Vol(Issue), pages. DOI
    """
    
    def __init__(self):
        super().__init__()
        self.format_name = "apa"
        
        # Regex patterns for APA citation components
        self.patterns = {
            # Author(s), year pattern - matches "Author, A. A., & Author, B. B. (Year)"
            "author_year": r"([^(]+)\s*\((\d{4}[a-z]?)\)",
            
            # Title pattern - matches the title after the year and period
            "title": r"\(\d{4}[a-z]?\)\.\s+([^.]+)",
            
            # Journal/source pattern - matches journal name and potentially volume/issue
            "journal": r"([A-Z][^,]+)(?:,\s*(\d+)(?:\((\d+[A-Za-z]?)\))?)?",
            
            # Pages pattern - matches page ranges in various formats
            "pages": r"(\d+)[-–](\d+)",
            
            # DOI pattern - matches DOI in various formats
            "doi": r"https?://doi\.org/(.+)$|DOI:\s*(.+)$|10\.\d{4,}/[-._;()/:A-Za-z0-9]+",
            
            # URL pattern - matches URLs in various formats
            "url": r"Retrieved from\s+(.+)$|Available at\s+(.+)$|https?://[^\s)\"]+",
        }
        
        # Complete APA reference pattern (comprehensive but may not catch all variations)
        self.apa_pattern = re.compile(
            r"([^(]+)\s*\((\d{4}[a-z]?)\)\.\s+([^.]+)\.\s+([^,]+)(?:,\s*(\d+)(?:\((\d+[A-Za-z]?)\))?)?,?\s*(?:(\d+[-–]\d+))?\.\s*(?:https?://doi\.org/(.+)|DOI:\s*(.+))?",
            re.DOTALL
        )
    
    def parse(self, text: str) -> Optional[Citation]:
        """Parse a single APA citation string.
        
        Args:
            text: A string containing a single APA citation
            
        Returns:
            Citation object if parsing successful, None otherwise
        """
        text = text.strip()
        
        # Try to match the complete pattern first
        match = self.apa_pattern.match(text)
        
        if match:
            # Extract all components from the match
            authors_str, year_str, title, source, volume, issue, pages, doi1, doi2 = match.groups()
            
            # Process authors (split by commas and '&')
            authors = self._process_authors(authors_str)
            
            # Process year
            year = int(re.sub(r'[a-z]', '', year_str)) if year_str else None
            
            # Process DOI (could be in either group)
            doi = doi1 or doi2
            
            # Create citation object
            citation = Citation(
                authors=authors,
                year=year,
                title=clean_title(title) if title else "",
                source=source.strip() if source else "",
                volume=volume,
                issue=issue,
                pages=pages,
                doi=doi,
                citation_type=self._determine_citation_type(text),
                citation_format="apa",
                citation_text=text
            )
            
            # Additional metadata extraction
            citation.url = self._extract_url(text)
            
            # Calculate confidence
            citation.confidence_score = self.calculate_confidence(citation)
            
            return citation
            
        # Fallback: try to extract components individually
        return self._fallback_parse(text)
    
    def _fallback_parse(self, text: str) -> Optional[Citation]:
        """Fallback method for when the main regex pattern doesn't match."""
        authors = self._extract_authors(text)
        year = extract_year(text)
        title = self._extract_title(text)
        source = self._extract_source(text)
        
        if authors and title and source:
            citation = Citation(
                authors=authors,
                year=year,
                title=title,
                source=source,
                citation_format="apa",
                citation_text=text
            )
            
            # Extract additional metadata
            citation.doi = extract_doi(text)
            citation.url = self._extract_url(text)
            citation.pages = extract_pages(text)
            volume, issue = extract_volume_issue(text)
            citation.volume = volume
            citation.issue = issue
            citation.citation_type = self._determine_citation_type(text)
            
            # Calculate confidence (will be lower for partial matches)
            citation.confidence_score = self.calculate_confidence(citation)
            
            return citation
        
        return None
    
    def extract_citations(self, text: str) -> List[Citation]:
        """Extract all APA citations from a larger text.
        
        Args:
            text: A string that may contain multiple APA citations
            
        Returns:
            List of Citation objects found in the text
        """
        citations = []
        
        # Look for a references section
        references_match = re.search(r'(?:References|Bibliography|Works Cited)[:.\n]+(.*)', text, re.IGNORECASE | re.DOTALL)
        if references_match:
            # If we found a references section, focus on that
            references_text = references_match.group(1)
            # Split by newlines (common format for reference lists)
            potential_citations = re.split(r'\n\s*\n|\n(?=[A-Z])', references_text)
        else:
            # Otherwise, try to find citations in the full text
            # Split by periods followed by multiple spaces or newlines, or by newlines followed by capital letters
            potential_citations = re.split(r'\.\s{2,}|\.\n+|\n(?=[A-Z])', text)
        
        for potential in potential_citations:
            # Skip very short strings
            if len(potential.strip()) < 20:
                continue
                
            # Basic check: does it look like it might be an APA citation?
            # Look for author-year pattern: text followed by year in parentheses
            if re.search(r'[A-Za-z]+.*\(\d{4}[a-z]?\)', potential):
                citation = self.parse(potential)
                if citation and citation.confidence_score > 0.5:
                    citations.append(citation)
        
        return citations
    
    def _process_authors(self, authors_str: str) -> List[str]:
        """Process author string into list of normalized author names."""
        # Handle the case with '&' - common in APA citations
        if '&' in authors_str:
            # Split the string at the '&' to separate the last author
            parts = authors_str.split('&')
            
            # Process all authors before the '&'
            main_authors = parts[0].strip()
            last_author = parts[1].strip()
            
            # Process the main authors (comma-separated list)
            authors = []
            
            # If there are commas in the main authors part
            if ',' in main_authors:
                # Split by commas
                main_parts = main_authors.split(',')
                
                # Process pairs of lastname, initials
                current_author = ""
                for i, part in enumerate(main_parts):
                    part = part.strip()
                    if not part:  # Skip empty parts
                        continue
                        
                    # If this looks like initials (short and contains periods)
                    if len(part) <= 5 and '.' in part:
                        # This is initials for the previous lastname
                        if current_author:
                            authors.append(f"{current_author}, {part}")
                            current_author = ""
                    else:
                        # This is a new lastname
                        if current_author:  # If we have a pending author, add it
                            authors.append(current_author)
                        current_author = part
                
                # Add any remaining author
                if current_author:
                    authors.append(current_author)
            else:
                # No commas, just a single author
                authors.append(main_authors)
            
            # Process the last author (after the '&')
            if ',' in last_author:
                last_parts = last_author.split(',')
                if len(last_parts) >= 2:
                    authors.append(f"{last_parts[0].strip()}, {last_parts[1].strip()}")
                else:
                    authors.append(last_author)
            else:
                authors.append(last_author)
        else:
            # No '&', process as a single author or comma-separated list
            authors = []
            if ',' in authors_str:
                parts = authors_str.split(',')
                
                # Process pairs of lastname, initials
                current_author = ""
                for i, part in enumerate(parts):
                    part = part.strip()
                    if not part:  # Skip empty parts
                        continue
                        
                    # If this looks like initials (short and contains periods)
                    if len(part) <= 5 and '.' in part:
                        # This is initials for the previous lastname
                        if current_author:
                            authors.append(f"{current_author}, {part}")
                            current_author = ""
                    else:
                        # This is a new lastname
                        if current_author:  # If we have a pending author, add it
                            authors.append(current_author)
                        current_author = part
                
                # Add any remaining author
                if current_author:
                    authors.append(current_author)
            else:
                # No commas, just a single author
                authors.append(authors_str.strip())
        
        # Filter out any empty strings and normalize
        return [normalize_author_name(author) for author in authors if author.strip()]
    
    def _extract_authors(self, text: str) -> List[str]:
        """Extract authors from citation text."""
        match = re.search(self.patterns["author_year"], text)
        if match:
            authors_str = match.group(1)
            return self._process_authors(authors_str)
        return []
    
    def _extract_title(self, text: str) -> str:
        """Extract title from citation text."""
        match = re.search(self.patterns["title"], text)
        if match:
            return clean_title(match.group(1))
        return ""
    
    def _extract_source(self, text: str) -> str:
        """Extract source/journal from citation text."""
        # Look for the source after the title
        parts = text.split('. ')
        if len(parts) >= 3:  # author+year, title, [source]
            source_part = parts[2].split(',')[0]
            return source_part.strip()
        
        # Alternative approach: look for journal pattern
        match = re.search(self.patterns["journal"], text)
        if match:
            return match.group(1).strip()
        
        return ""
    
    def _extract_url(self, text: str) -> Optional[str]:
        """Extract URL from citation text."""
        urls = extract_urls(text)
        if urls:
            return urls[0]
        return None
    
    def _determine_citation_type(self, text: str) -> str:
        """Determine the type of citation (article, book, chapter, etc.)."""
        # Look for indicators of citation type
        if re.search(r'journal|article|periodical', text.lower()):
            return "article"
        if re.search(r'book|press', text.lower()):
            return "book"
        if re.search(r'chapter|in\s+[A-Z]|\(Eds?\.\)', text.lower()):
            return "book_chapter"
        if re.search(r'conference|proceedings|symposium', text.lower()):
            return "conference"
        if re.search(r'thesis|dissertation', text.lower()):
            return "thesis"
        if re.search(r'report|technical', text.lower()):
            return "report"
        if re.search(r'website|retrieved from|available at|http', text.lower()):
            return "web"
        
        # Default to article as most common type
        return "article"
    
    def calculate_confidence(self, citation: Citation) -> float:
        """Calculate confidence score for a parsed APA citation.
        
        Args:
            citation: A Citation object to evaluate
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
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
