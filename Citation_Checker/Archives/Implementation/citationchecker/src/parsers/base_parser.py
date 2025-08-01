from abc import ABC, abstractmethod
from typing import List, Optional
from src.models.citation import Citation

class BaseCitationParser(ABC):
    """Abstract base class for all citation parsers.
    
    This class defines the interface that all citation parser implementations
    must follow, ensuring consistent behavior across different citation formats.
    """
    
    def __init__(self):
        """Initialize the base parser."""
        self.format_name = "unknown"
    
    @abstractmethod
    def parse(self, text: str) -> Optional[Citation]:
        """Parse a single citation string and return a Citation object.
        
        Args:
            text: A string containing a single citation
            
        Returns:
            Citation object if parsing successful, None otherwise
        """
        pass
    
    @abstractmethod
    def extract_citations(self, text: str) -> List[Citation]:
        """Extract all citations from a larger text.
        
        Args:
            text: A string that may contain multiple citations
            
        Returns:
            List of Citation objects found in the text
        """
        pass
    
    def calculate_confidence(self, citation: Citation) -> float:
        """Calculate confidence score for a parsed citation.
        
        Args:
            citation: A Citation object to evaluate
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        # Basic implementation - override for format-specific logic
        score = 0.0
        required_fields = ["authors", "title", "source"]
        
        # Check if required fields are present
        for field in required_fields:
            if getattr(citation, field):
                score += 0.25
        
        # Additional score for year
        if citation.year:
            score += 0.25
        
        return min(score, 1.0)