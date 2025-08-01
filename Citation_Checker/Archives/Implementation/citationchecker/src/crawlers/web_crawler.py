"""
General Web Crawler

This module implements a general-purpose web crawler that can extract content
from most websites using multiple content extraction strategies.
"""

import re
from typing import Dict, Any
from urllib.parse import urlparse
from bs4 import BeautifulSoup

from .base_crawler import BaseCrawler

class WebCrawler(BaseCrawler):
    """General-purpose web crawler for extracting content from websites.
    
    This crawler uses multiple strategies to extract the main content from web pages,
    including readability algorithms and heuristic-based content detection.
    """
    
    def __init__(self, **kwargs):
        """Initialize the web crawler."""
        super().__init__(**kwargs)
        self.name = "general_web"
    
    def can_crawl(self, url: str) -> bool:
        """Check if this crawler can handle the given URL.
        
        This is a general crawler, so it can handle any HTTP/HTTPS URL.
        
        Args:
            url: The URL to check
            
        Returns:
            True if the URL is HTTP/HTTPS, False otherwise
        """
        try:
            parsed = urlparse(url)
            return parsed.scheme.lower() in ['http', 'https']
        except:
            return False
    
    def extract_content(self, html: str, url: str) -> Dict[str, Any]:
        """Extract structured content from HTML.
        
        Uses multiple strategies to extract the main content:
        1. Try newspaper3k for article extraction
        2. Try trafilatura for general content extraction
        3. Fall back to heuristic-based extraction
        
        Args:
            html: Raw HTML content
            url: The URL the content was retrieved from
            
        Returns:
            Dictionary containing extracted content and metadata
        """
        # Start with basic metadata extraction
        metadata = self._extract_metadata_from_html(html, url)
        content = ""
        
        # Strategy 1: Try newspaper3k for article-like content
        try:
            content = self._extract_with_newspaper(html, url)
            if content and len(content.strip()) > 100:
                metadata['extraction_method'] = 'newspaper3k'
                return {'content': content, 'metadata': metadata}
        except Exception as e:
            pass
        
        # Strategy 2: Try trafilatura for general content extraction
        try:
            content = self._extract_with_trafilatura(html, url)
            if content and len(content.strip()) > 100:
                metadata['extraction_method'] = 'trafilatura'
                return {'content': content, 'metadata': metadata}
        except Exception as e:
            pass
        
        # Strategy 3: Fall back to heuristic-based extraction
        try:
            content = self._extract_with_heuristics(html, url)
            metadata['extraction_method'] = 'heuristics'
            return {'content': content, 'metadata': metadata}
        except Exception as e:
            # Last resort: return cleaned HTML text
            soup = BeautifulSoup(html, 'html.parser')
            content = self._clean_text(soup.get_text())
            metadata['extraction_method'] = 'fallback'
            return {'content': content, 'metadata': metadata}
    
    def _extract_with_newspaper(self, html: str, url: str) -> str:
        """Extract content using newspaper3k library.
        
        Args:
            html: HTML content
            url: Source URL
            
        Returns:
            Extracted text content
        """
        try:
            from newspaper import Article
            
            article = Article(url)
            article.set_html(html)
            article.parse()
            
            # Combine title and text
            content_parts = []
            if article.title:
                content_parts.append(article.title)
            if article.text:
                content_parts.append(article.text)
            
            return '\n\n'.join(content_parts)
        except ImportError:
            raise Exception("newspaper3k not available")
        except Exception as e:
            raise Exception(f"newspaper3k extraction failed: {str(e)}")
    
    def _extract_with_trafilatura(self, html: str, url: str) -> str:
        """Extract content using trafilatura library.
        
        Args:
            html: HTML content
            url: Source URL
            
        Returns:
            Extracted text content
        """
        try:
            import trafilatura
            
            # Extract main content
            content = trafilatura.extract(html, include_comments=False, include_tables=True)
            
            if not content:
                raise Exception("No content extracted")
            
            return content
        except ImportError:
            raise Exception("trafilatura not available")
        except Exception as e:
            raise Exception(f"trafilatura extraction failed: {str(e)}")
    
    def _extract_with_heuristics(self, html: str, url: str) -> str:
        """Extract content using heuristic-based approach.
        
        This method uses various heuristics to identify and extract the main content
        from a web page, such as looking for common content containers and removing
        navigation, sidebar, and footer elements.
        
        Args:
            html: HTML content
            url: Source URL
            
        Returns:
            Extracted text content
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove unwanted elements
        unwanted_tags = ['script', 'style', 'nav', 'header', 'footer', 'aside', 'advertisement']
        for tag in unwanted_tags:
            for element in soup.find_all(tag):
                element.decompose()
        
        # Remove elements with common unwanted classes/ids
        unwanted_selectors = [
            '[class*="nav"]', '[class*="menu"]', '[class*="sidebar"]',
            '[class*="footer"]', '[class*="header"]', '[class*="ad"]',
            '[class*="advertisement"]', '[class*="social"]', '[class*="share"]',
            '[id*="nav"]', '[id*="menu"]', '[id*="sidebar"]',
            '[id*="footer"]', '[id*="header"]', '[id*="ad"]'
        ]
        
        for selector in unwanted_selectors:
            try:
                for element in soup.select(selector):
                    element.decompose()
            except:
                continue
        
        # Look for main content containers
        content_selectors = [
            'main', 'article', '[role="main"]',
            '.content', '.main-content', '.post-content', '.entry-content',
            '#content', '#main-content', '#post-content', '#entry-content',
            '.article-body', '.story-body', '.post-body'
        ]
        
        main_content = None
        for selector in content_selectors:
            try:
                element = soup.select_one(selector)
                if element:
                    main_content = element
                    break
            except:
                continue
        
        # If no main content container found, use the body
        if not main_content:
            main_content = soup.find('body') or soup
        
        # Extract text and clean it
        text = main_content.get_text(separator=' ', strip=True)
        
        # Additional cleaning
        text = self._clean_extracted_text(text)
        
        return text
    
    def _clean_extracted_text(self, text: str) -> str:
        """Clean extracted text content.
        
        Args:
            text: Raw extracted text
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove common navigation text patterns
        nav_patterns = [
            r'Skip to (?:main )?content',
            r'Menu',
            r'Home\s+About\s+Contact',
            r'Copyright.*?(?:\d{4}|\n)',
            r'All rights reserved',
            r'Privacy Policy',
            r'Terms of Service',
            r'Cookie Policy'
        ]
        
        for pattern in nav_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        # Remove repeated short lines (often navigation)
        lines = text.split('\n')
        cleaned_lines = []
        prev_line = ""
        
        for line in lines:
            line = line.strip()
            if len(line) > 10 or (len(line) > 0 and line != prev_line):
                cleaned_lines.append(line)
            prev_line = line
        
        text = '\n'.join(cleaned_lines)
        
        # Final cleanup
        text = self._clean_text(text)
        
        return text
    
    def _extract_structured_data(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract structured data from the page.
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            Dictionary containing structured data
        """
        structured_data = {}
        
        # Extract JSON-LD structured data
        json_ld_scripts = soup.find_all('script', type='application/ld+json')
        if json_ld_scripts:
            import json
            json_ld_data = []
            for script in json_ld_scripts:
                try:
                    data = json.loads(script.string)
                    json_ld_data.append(data)
                except:
                    continue
            if json_ld_data:
                structured_data['json_ld'] = json_ld_data
        
        # Extract Open Graph data
        og_data = {}
        og_tags = soup.find_all('meta', property=lambda x: x and x.startswith('og:'))
        for tag in og_tags:
            property_name = tag.get('property', '').replace('og:', '')
            content = tag.get('content')
            if property_name and content:
                og_data[property_name] = content
        
        if og_data:
            structured_data['open_graph'] = og_data
        
        # Extract Twitter Card data
        twitter_data = {}
        twitter_tags = soup.find_all('meta', attrs={'name': lambda x: x and x.startswith('twitter:')})
        for tag in twitter_tags:
            name = tag.get('name', '').replace('twitter:', '')
            content = tag.get('content')
            if name and content:
                twitter_data[name] = content
        
        if twitter_data:
            structured_data['twitter_card'] = twitter_data
        
        return structured_data
