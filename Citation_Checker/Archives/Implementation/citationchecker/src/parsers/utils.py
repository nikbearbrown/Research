import re
from typing import List, Optional, Tuple, Dict

def normalize_author_name(author: str) -> str:
    """Normalize author name format.
    
    Args:
        author: Author name in various formats
        
    Returns:
        Normalized author name
    """
    # Handle "Lastname, F. M." format
    if ',' in author:
        parts = author.split(',', 1)
        lastname = parts[0].strip()
        initials = parts[1].strip() if len(parts) > 1 else ""
        return f"{lastname}, {initials}"
    
    # Handle "F. M. Lastname" format
    parts = author.split()
    if len(parts) > 1 and any(p.endswith('.') for p in parts[:-1]):
        lastname = parts[-1].strip()
        initials = ' '.join(parts[:-1]).strip()
        return f"{lastname}, {initials}"
    
    return author.strip()

def extract_urls(text: str) -> List[str]:
    """Extract all URLs from text.
    
    Args:
        text: Text that may contain URLs
        
    Returns:
        List of URLs found in the text
    """
    # Regex pattern for URLs, including those preceded by "Retrieved from" or "Available at"
    url_pattern = r'(?:Retrieved from|Available at)?\s*(https?://[^\s)"]+)'
    urls = re.findall(url_pattern, text)
    return urls

def extract_year(text: str) -> Optional[int]:
    """Extract a year (4 digits) from text.
    
    Args:
        text: Text that may contain a year
        
    Returns:
        Year as integer if found, None otherwise
    """
    # Look for years in parentheses first (common in citations)
    year_match = re.search(r'\((\d{4})[a-z]?\)', text)
    if year_match:
        return int(year_match.group(1))
    
    # Then look for any 4-digit number that could be a year (1900-2099)
    year_match = re.search(r'\b(19|20)\d{2}\b', text)
    if year_match:
        return int(year_match.group(0))
    
    return None

def extract_doi(text: str) -> Optional[str]:
    """Extract a DOI from text.
    
    Args:
        text: Text that may contain a DOI
        
    Returns:
        DOI string if found, None otherwise
    """
    # Look for DOI in standard format
    doi_match = re.search(r'(?:https?://doi\.org/|DOI:\s*)([^\s]+)', text, re.IGNORECASE)
    if doi_match:
        return doi_match.group(1).strip()
    
    # Try alternate format
    doi_match = re.search(r'\b10\.\d{4,}\/[-._;()/:A-Za-z0-9]+\b', text)
    if doi_match:
        return doi_match.group(0).strip()
    
    return None

def clean_title(title: str) -> str:
    """Clean a title string by removing unnecessary punctuation.
    
    Args:
        title: Title string that may contain extra punctuation
        
    Returns:
        Cleaned title string
    """
    # Remove trailing periods, commas, etc.
    title = re.sub(r'[.,;:!?]+$', '', title.strip())
    
    # Remove enclosing quotes if present
    if (title.startswith('"') and title.endswith('"')) or \
       (title.startswith("'") and title.endswith("'")):
        title = title[1:-1]
    
    return title.strip()

def extract_pages(text: str) -> Optional[str]:
    """Extract page numbers from text.
    
    Args:
        text: Text that may contain page numbers
        
    Returns:
        Page range as string if found, None otherwise
    """
    # Look for page ranges (e.g., 45-67, pp. 23-45)
    pages_match = re.search(r'(?:p\.?|pp\.?)\s*(\d+[-–—]\d+|\d+)', text)
    if pages_match:
        return pages_match.group(1).strip()
    
    # Alternate format often found at end of citations
    pages_match = re.search(r'[,.]\s*(\d+[-–—]\d+)\.?$', text)
    if pages_match:
        return pages_match.group(1).strip()
    
    return None

def extract_volume_issue(text: str) -> Tuple[Optional[str], Optional[str]]:
    """Extract volume and issue numbers from text.
    
    Args:
        text: Text that may contain volume and issue numbers
        
    Returns:
        Tuple of (volume, issue), either may be None
    """
    # Common format: Journal Name, 15(2), 45-67
    vol_issue_match = re.search(r'(\d+)\s*\((\d+[A-Za-z]?)\)', text)
    if vol_issue_match:
        return vol_issue_match.group(1), vol_issue_match.group(2)
    
    # Format with just volume: Journal Name, 15, 45-67
    vol_match = re.search(r'[,\s](\d+)[,\s]', text)
    if vol_match:
        return vol_match.group(1), None
    
    return None, None