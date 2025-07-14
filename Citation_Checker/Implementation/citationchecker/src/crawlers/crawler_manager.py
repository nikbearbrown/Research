"""
Crawler Manager

This module provides a unified interface for managing multiple web crawlers
and selecting the appropriate crawler for each URL.
"""

import time
import logging
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed

from .base_crawler import BaseCrawler, CrawlResult
from .web_crawler import WebCrawler
from .academic_crawler import AcademicCrawler

logger = logging.getLogger(__name__)

class CrawlerManager:
    """Manager class that coordinates multiple crawlers and provides a unified interface.
    
    This class automatically selects the most appropriate crawler for each URL
    and provides methods for crawling single URLs or batches of URLs.
    """
    
    def __init__(self, max_workers: int = 5, default_timeout: int = 30):
        """Initialize the crawler manager.
        
        Args:
            max_workers: Maximum number of concurrent crawling threads
            default_timeout: Default timeout for crawling operations
        """
        self.max_workers = max_workers
        self.default_timeout = default_timeout
        
        # Initialize available crawlers
        self.crawlers = [
            AcademicCrawler(timeout=default_timeout),
            WebCrawler(timeout=default_timeout),
        ]
        
        # Statistics tracking
        self.stats = {
            'total_crawls': 0,
            'successful_crawls': 0,
            'failed_crawls': 0,
            'crawler_usage': {},
            'domain_stats': {},
            'total_time': 0.0
        }
    
    def crawl_url(self, url: str) -> CrawlResult:
        """Crawl a single URL using the most appropriate crawler.
        
        Args:
            url: The URL to crawl
            
        Returns:
            CrawlResult object containing the crawl results
        """
        start_time = time.time()
        
        try:
            # Select the appropriate crawler
            crawler = self._select_crawler(url)
            if not crawler:
                return CrawlResult(
                    url=url,
                    success=False,
                    error="No suitable crawler found for URL"
                )
            
            # Perform the crawl
            result = crawler.crawl(url)
            
            # Update statistics
            self._update_stats(url, result, crawler, time.time() - start_time)
            
            return result
            
        except Exception as e:
            logger.error(f"Error in crawler manager for {url}: {str(e)}")
            result = CrawlResult(
                url=url,
                success=False,
                error=f"Crawler manager error: {str(e)}"
            )
            self._update_stats(url, result, None, time.time() - start_time)
            return result
    
    def crawl_urls(self, urls: List[str], max_workers: Optional[int] = None) -> List[CrawlResult]:
        """Crawl multiple URLs concurrently.
        
        Args:
            urls: List of URLs to crawl
            max_workers: Maximum number of concurrent workers (defaults to instance setting)
            
        Returns:
            List of CrawlResult objects in the same order as input URLs
        """
        if not urls:
            return []
        
        workers = max_workers or self.max_workers
        results = [None] * len(urls)  # Pre-allocate results list to maintain order
        
        with ThreadPoolExecutor(max_workers=workers) as executor:
            # Submit all crawl tasks
            future_to_index = {
                executor.submit(self.crawl_url, url): i 
                for i, url in enumerate(urls)
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_index):
                index = future_to_index[future]
                try:
                    result = future.result()
                    results[index] = result
                except Exception as e:
                    logger.error(f"Error crawling URL at index {index}: {str(e)}")
                    results[index] = CrawlResult(
                        url=urls[index],
                        success=False,
                        error=f"Concurrent crawl error: {str(e)}"
                    )
        
        return results
    
    def crawl_from_citations(self, citations: List[Dict[str, Any]]) -> List[CrawlResult]:
        """Crawl URLs extracted from citation objects.
        
        Args:
            citations: List of citation dictionaries containing URL information
            
        Returns:
            List of CrawlResult objects
        """
        urls = []
        for citation in citations:
            # Extract URL from citation
            url = citation.get('url') or citation.get('doi_url')
            if url:
                urls.append(url)
        
        if not urls:
            logger.warning("No URLs found in citations")
            return []
        
        return self.crawl_urls(urls)
    
    def _select_crawler(self, url: str) -> Optional[BaseCrawler]:
        """Select the most appropriate crawler for a given URL.
        
        Args:
            url: The URL to crawl
            
        Returns:
            The most suitable crawler, or None if no crawler can handle the URL
        """
        # Try crawlers in order of specificity (most specific first)
        for crawler in self.crawlers:
            if crawler.can_crawl(url):
                return crawler
        
        return None
    
    def _update_stats(self, url: str, result: CrawlResult, crawler: Optional[BaseCrawler], 
                     crawl_time: float):
        """Update crawling statistics.
        
        Args:
            url: The crawled URL
            result: The crawl result
            crawler: The crawler that was used
            crawl_time: Time taken for the crawl
        """
        self.stats['total_crawls'] += 1
        self.stats['total_time'] += crawl_time
        
        if result.success:
            self.stats['successful_crawls'] += 1
        else:
            self.stats['failed_crawls'] += 1
        
        # Track crawler usage
        if crawler:
            crawler_name = getattr(crawler, 'name', crawler.__class__.__name__)
            self.stats['crawler_usage'][crawler_name] = (
                self.stats['crawler_usage'].get(crawler_name, 0) + 1
            )
        
        # Track domain statistics
        try:
            domain = urlparse(url).netloc.lower()
            if domain not in self.stats['domain_stats']:
                self.stats['domain_stats'][domain] = {
                    'total': 0, 'successful': 0, 'failed': 0, 'avg_time': 0.0
                }
            
            domain_stats = self.stats['domain_stats'][domain]
            domain_stats['total'] += 1
            
            if result.success:
                domain_stats['successful'] += 1
            else:
                domain_stats['failed'] += 1
            
            # Update average time (running average)
            domain_stats['avg_time'] = (
                (domain_stats['avg_time'] * (domain_stats['total'] - 1) + crawl_time) 
                / domain_stats['total']
            )
            
        except Exception as e:
            logger.warning(f"Error updating domain stats for {url}: {str(e)}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get crawling statistics.
        
        Returns:
            Dictionary containing crawling statistics
        """
        stats = self.stats.copy()
        
        # Add computed statistics
        if stats['total_crawls'] > 0:
            stats['success_rate'] = stats['successful_crawls'] / stats['total_crawls']
            stats['avg_crawl_time'] = stats['total_time'] / stats['total_crawls']
        else:
            stats['success_rate'] = 0.0
            stats['avg_crawl_time'] = 0.0
        
        return stats
    
    def reset_stats(self):
        """Reset all crawling statistics."""
        self.stats = {
            'total_crawls': 0,
            'successful_crawls': 0,
            'failed_crawls': 0,
            'crawler_usage': {},
            'domain_stats': {},
            'total_time': 0.0
        }
    
    def add_crawler(self, crawler: BaseCrawler):
        """Add a custom crawler to the manager.
        
        Args:
            crawler: The crawler to add
        """
        self.crawlers.insert(0, crawler)  # Insert at beginning for higher priority
    
    def remove_crawler(self, crawler_class):
        """Remove a crawler by class type.
        
        Args:
            crawler_class: The class of crawler to remove
        """
        self.crawlers = [c for c in self.crawlers if not isinstance(c, crawler_class)]
    
    def get_supported_domains(self) -> List[str]:
        """Get a list of all domains supported by the available crawlers.
        
        Returns:
            List of supported domain patterns
        """
        supported_domains = []
        
        for crawler in self.crawlers:
            if hasattr(crawler, 'academic_domains'):
                supported_domains.extend(crawler.academic_domains.keys())
            elif hasattr(crawler, 'supported_domains'):
                supported_domains.extend(crawler.supported_domains)
            else:
                # For general crawlers, indicate they support all HTTP/HTTPS
                supported_domains.append("*")
        
        return list(set(supported_domains))
    
    def test_crawler_selection(self, urls: List[str]) -> Dict[str, str]:
        """Test which crawler would be selected for each URL without actually crawling.
        
        Args:
            urls: List of URLs to test
            
        Returns:
            Dictionary mapping URLs to crawler names
        """
        results = {}
        
        for url in urls:
            crawler = self._select_crawler(url)
            if crawler:
                crawler_name = getattr(crawler, 'name', crawler.__class__.__name__)
                results[url] = crawler_name
            else:
                results[url] = "No suitable crawler"
        
        return results
    
    def close(self):
        """Close all crawlers and clean up resources."""
        for crawler in self.crawlers:
            try:
                crawler.close()
            except Exception as e:
                logger.warning(f"Error closing crawler {crawler.__class__.__name__}: {str(e)}")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
