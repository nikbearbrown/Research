from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime

@dataclass
class Citation:
    """Standardized model for storing parsed citations.
    
    This class represents the common structure for citations across different
    formats (APA, MLA, Chicago, etc.) and provides a consistent interface for
    the verification system to work with.
    """
    
    # Basic citation components
    authors: List[str]
    year: Optional[int]
    title: str
    source: str
    
    # Additional metadata
    doi: Optional[str] = None
    url: Optional[str] = None
    volume: Optional[str] = None
    issue: Optional[str] = None
    pages: Optional[str] = None
    publisher: Optional[str] = None
    
    # Citation metadata
    citation_type: str = "unknown"  # article, book, chapter, etc.
    citation_format: str = "unknown"  # apa, mla, chicago, etc.
    citation_text: str = ""  # The original citation text
    confidence_score: float = 0.0  # How confident we are in the parsing (0-1)
    
    def to_dict(self):
        """Convert the citation to a dictionary."""
        return {
            "authors": self.authors,
            "year": self.year,
            "title": self.title,
            "source": self.source,
            "doi": self.doi,
            "url": self.url,
            "volume": self.volume,
            "issue": self.issue,
            "pages": self.pages,
            "publisher": self.publisher,
            "citation_type": self.citation_type,
            "citation_format": self.citation_format,
            "citation_text": self.citation_text,
            "confidence_score": self.confidence_score
        }
    
    def __str__(self):
        """String representation of the citation."""
        return f"Citation({self.citation_format}): {', '.join(self.authors)} ({self.year}). {self.title}. {self.source}."