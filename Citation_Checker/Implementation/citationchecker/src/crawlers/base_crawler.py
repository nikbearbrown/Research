"""
Base Crawler Class

This module defines the abstract base class for all web crawlers in the Citation Checker project.
It provides common functionality and defines the interface that all crawler implementations must follow.
"""

import time
import logging
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from urllib.parse import urlparse, urljoin
from urllib.robotparser import RobotFileParser
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CrawlResult:
    """Data class to hold the results of a web crawl operation."""
    
    def __init__(self, url: str, success: bool = False, content: str = "", 
                 metadata: Optional[Dict[str, Any]] = None, error: Optional[str] = None,
                 status_code: Optional[int] = None, response_time: Optional[float] = None):
        self.url = url
        self.success = success
        self.content = content
        self.metadata = metadata or {}
        self.error = error
        self.status_code = status_code
        self.response_time = response_time
        self.crawl_timestamp = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the crawl result to a dictionary."""
        return {
            'url': self.url,
            'success': self.success,
            'content': self.content,
            'metadata': self.metadata,
            'error': self.error,
            'status_code': self.status_code,
            'response_time': self.response_time,
            'crawl_timestamp': self.crawl_timestamp
        }

class BaseCrawler(ABC):
    """Abstract base class for all web crawlers.
    
    This class defines the interface that all crawler implementations must follow
    and provides common functionality for web crawling operations.
    """
    
    def __init__(self, user_agent: str = None, timeout: int = 30, max_retries: int = 3):
        """Initialize the base crawler.
        
        Args:
            user_agent: User agent string to use for requests
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
        """
        self.user_agent = user_agent or "CitationChecker/1.0 (Educational Research Tool)"
        self.timeout = timeout
        self.max_retries = max_retries
        
        # Configure session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set default headers
        self.session.headers.update({
            'User-Agent': self.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        
        # Cache for robots.txt files
        self._robots_cache = {}
    
    @abstractmethod
    def can_crawl(self, url: str) -> bool:
        """Check if this crawler can handle the given URL.
        
        Args:
            url: The URL to check
            
        Returns:
            True if this crawler can handle the URL, False otherwise
        """
        pass
    
    @abstractmethod
    def extract_content(self, html: str, url: str) -> Dict[str, Any]:
        """Extract structured content from HTML.
        
        Args:
            html: Raw HTML content
            url: The URL the content was retrieved from
            
        Returns:
            Dictionary containing extracted content and metadata
        """
        pass
    
    def crawl(self, url: str) -> CrawlResult:
        """Crawl a single URL and extract content.
        
        Args:
            url: The URL to crawl
            
        Returns:
            CrawlResult object containing the crawl results
        """
        start_time = time.time()
        
        try:
            # Check if crawling is allowed
            if not self._is_crawling_allowed(url):
                return CrawlResult(
                    url=url,
                    success=False,
                    error="Crawling not allowed by robots.txt"
                )
            
            # Make the request
            logger.info(f"Crawling URL: {url}")
            response = self.session.get(url, timeout=self.timeout)
            response_time = time.time() - start_time
            
            # Check if request was successful
            response.raise_for_status()
            
            # Extract content using the specific crawler implementation
            extracted_data = self.extract_content(response.text, url)
            
            return CrawlResult(
                url=url,
                success=True,
                content=extracted_data.get('content', ''),
                metadata=extracted_data.get('metadata', {}),
                status_code=response.status_code,
                response_time=response_time
            )
            
        except requests.exceptions.RequestException as e:
            response_time = time.time() - start_time
            logger.error(f"Error crawling {url}: {str(e)}")
            return CrawlResult(
                url=url,
                success=False,
                error=str(e),
                response_time=response_time
            )
        except Exception as e:
            response_time = time.time() - start_time
            logger.error(f"Unexpected error crawling {url}: {str(e)}")
            return CrawlResult(
                url=url,
                success=False,
                error=f"Unexpected error: {str(e)}",
                response_time=response_time
            )
    
    def crawl_multiple(self, urls: List[str]) -> List[CrawlResult]:
        """Crawl multiple URLs.
        
        Args:
            urls: List of URLs to crawl
            
        Returns:
            List of CrawlResult objects
        """
        results = []
        for url in urls:
            # Add delay between requests to be respectful
            if results:  # Don't delay before the first request
                time.sleep(1)
            
            result = self.crawl(url)
            results.append(result)
        
        return results
    
    def _is_crawling_allowed(self, url: str) -> bool:
        """Check if crawling is allowed by robots.txt.
        
        Args:
            url: The URL to check
            
        Returns:
            True if crawling is allowed, False otherwise
        """
        try:
            parsed_url = urlparse(url)
            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
            
            # Check cache first
            if base_url in self._robots_cache:
                rp = self._robots_cache[base_url]
            else:
                # Fetch and parse robots.txt
                robots_url = urljoin(base_url, '/robots.txt')
                rp = RobotFileParser()
                rp.set_url(robots_url)
                try:
                    rp.read()
                    self._robots_cache[base_url] = rp
                except:
                    # If we can't read robots.txt, assume crawling is allowed
                    logger.warning(f"Could not read robots.txt for {base_url}")
                    return True
            
            # Check if our user agent can fetch this URL
            return rp.can_fetch(self.user_agent, url)
            
        except Exception as e:
            logger.warning(f"Error checking robots.txt for {url}: {str(e)}")
            # If we can't check robots.txt, err on the side of caution but allow crawling
            return True
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted text.
        
        Args:
            text: Raw text to clean
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Remove extra whitespace and normalize line breaks
        text = ' '.join(text.split())
        
        # Remove common HTML entities that might have been missed
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&quot;', '"')
        text = text.replace('&#39;', "'")
        
        return text.strip()
    
    def _extract_metadata_from_html(self, html: str, url: str) -> Dict[str, Any]:
        """Extract basic metadata from HTML.
        
        Args:
            html: HTML content
            url: Source URL
            
        Returns:
            Dictionary containing metadata
        """
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(html, 'html.parser')
        metadata = {}
        
        # Extract title
        title_tag = soup.find('title')
        if title_tag:
            metadata['title'] = self._clean_text(title_tag.get_text())
        
        # Extract meta tags
        meta_tags = soup.find_all('meta')
        for tag in meta_tags:
            name = tag.get('name') or tag.get('property')
            content = tag.get('content')
            if name and content:
                metadata[name.lower()] = content
        
        # Extract canonical URL
        canonical = soup.find('link', rel='canonical')
        if canonical and canonical.get('href'):
            metadata['canonical_url'] = canonical['href']
        
        # Extract language
        html_tag = soup.find('html')
        if html_tag and html_tag.get('lang'):
            metadata['language'] = html_tag['lang']
        
        return metadata
    
    def close(self):
        """Close the crawler and clean up resources."""
        if hasattr(self, 'session'):
            self.session.close()
