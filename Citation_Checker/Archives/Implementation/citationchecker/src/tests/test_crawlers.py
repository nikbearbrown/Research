"""
Test Suite for Web Crawlers

This module contains comprehensive tests for the web crawling functionality,
including unit tests for individual crawlers and integration tests.
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

from src.crawlers.base_crawler import BaseCrawler, CrawlResult
from src.crawlers.web_crawler import WebCrawler
from src.crawlers.academic_crawler import AcademicCrawler
from src.crawlers.crawler_manager import CrawlerManager

class TestCrawlResult:
    """Test the CrawlResult data class."""
    
    def test_crawl_result_creation(self):
        """Test creating a CrawlResult object."""
        result = CrawlResult(
            url="https://example.com",
            success=True,
            content="Test content",
            metadata={"title": "Test Title"},
            status_code=200,
            response_time=1.5
        )
        
        assert result.url == "https://example.com"
        assert result.success is True
        assert result.content == "Test content"
        assert result.metadata["title"] == "Test Title"
        assert result.status_code == 200
        assert result.response_time == 1.5
        assert result.error is None
        assert isinstance(result.crawl_timestamp, float)
    
    def test_crawl_result_to_dict(self):
        """Test converting CrawlResult to dictionary."""
        result = CrawlResult(
            url="https://example.com",
            success=True,
            content="Test content"
        )
        
        result_dict = result.to_dict()
        
        assert isinstance(result_dict, dict)
        assert result_dict["url"] == "https://example.com"
        assert result_dict["success"] is True
        assert result_dict["content"] == "Test content"
        assert "crawl_timestamp" in result_dict

class TestWebCrawler:
    """Test the WebCrawler class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.crawler = WebCrawler()
    
    def teardown_method(self):
        """Clean up after tests."""
        self.crawler.close()
    
    def test_can_crawl_http_urls(self):
        """Test that WebCrawler can handle HTTP/HTTPS URLs."""
        assert self.crawler.can_crawl("https://example.com")
        assert self.crawler.can_crawl("http://example.com")
        assert not self.crawler.can_crawl("ftp://example.com")
        assert not self.crawler.can_crawl("invalid-url")
    
    @patch('src.crawlers.web_crawler.BeautifulSoup')
    def test_extract_content_with_heuristics(self, mock_soup):
        """Test content extraction using heuristics."""
        # Mock HTML structure
        mock_soup_instance = Mock()
        mock_soup.return_value = mock_soup_instance
        
        # Mock main content element
        mock_main = Mock()
        mock_main.get_text.return_value = "This is the main content of the page."
        mock_soup_instance.select_one.return_value = mock_main
        
        # Mock metadata extraction
        with patch.object(self.crawler, '_extract_metadata_from_html') as mock_meta:
            mock_meta.return_value = {"title": "Test Page"}
            
            result = self.crawler.extract_content("<html>test</html>", "https://example.com")
            
            assert "content" in result
            assert "metadata" in result
            assert result["metadata"]["extraction_method"] == "heuristics"
    
    @patch('requests.Session.get')
    def test_crawl_successful(self, mock_get):
        """Test successful crawling of a URL."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "<html><title>Test</title><body>Content</body></html>"
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = self.crawler.crawl("https://example.com")
        
        assert result.success is True
        assert result.url == "https://example.com"
        assert result.status_code == 200
        assert isinstance(result.response_time, float)
    
    @patch('requests.Session.get')
    def test_crawl_request_error(self, mock_get):
        """Test crawling with request error."""
        # Mock request exception
        mock_get.side_effect = Exception("Connection error")
        
        result = self.crawler.crawl("https://example.com")
        
        assert result.success is False
        assert "Connection error" in result.error
        assert result.url == "https://example.com"

class TestAcademicCrawler:
    """Test the AcademicCrawler class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.crawler = AcademicCrawler()
    
    def teardown_method(self):
        """Clean up after tests."""
        self.crawler.close()
    
    def test_can_crawl_academic_domains(self):
        """Test that AcademicCrawler recognizes academic domains."""
        assert self.crawler.can_crawl("https://arxiv.org/abs/2101.00001")
        assert self.crawler.can_crawl("https://pubmed.ncbi.nlm.nih.gov/12345")
        assert self.crawler.can_crawl("https://ieeexplore.ieee.org/document/12345")
        assert self.crawler.can_crawl("https://dl.acm.org/doi/10.1145/12345")
        assert not self.crawler.can_crawl("https://example.com")
        assert not self.crawler.can_crawl("https://google.com")
    
    def test_extract_arxiv_content(self):
        """Test extraction of arXiv paper content."""
        # Mock arXiv HTML structure
        arxiv_html = """
        <html>
            <h1 class="title">Title: Test Paper Title</h1>
            <div class="authors">
                <a href="#">John Smith</a>, <a href="#">Jane Doe</a>
            </div>
            <blockquote class="abstract">
                Abstract: This is a test abstract for the paper.
            </blockquote>
            <div class="dateline">(Submitted on 1 Jan 2023)</div>
            <td class="tablecell subjects">Computer Science; Machine Learning</td>
        </html>
        """
        
        result = self.crawler._extract_arxiv(arxiv_html, "https://arxiv.org/abs/2301.00001")
        
        assert result["metadata"]["source"] == "arXiv"
        assert result["metadata"]["title"] == "Test Paper Title"
        assert "John Smith" in result["metadata"]["authors"]
        assert "Jane Doe" in result["metadata"]["authors"]
        assert "This is a test abstract" in result["content"]
        assert result["metadata"]["extraction_method"] == "arxiv_specific"
    
    def test_extract_pubmed_content(self):
        """Test extraction of PubMed article content."""
        # Mock PubMed HTML structure
        pubmed_html = """
        <html>
            <h1 class="heading-title">Test Medical Paper</h1>
            <div class="authors-list">
                <a class="full-name">Dr. Smith</a>
                <a class="full-name">Dr. Johnson</a>
            </div>
            <div class="abstract-content">
                This is the abstract of the medical paper.
            </div>
            <button id="full-view-journal-trigger">Nature Medicine</button>
            <span class="citation-doi">doi: 10.1038/s41591-023-01234-5</span>
        </html>
        """
        
        result = self.crawler._extract_pubmed(pubmed_html, "https://pubmed.ncbi.nlm.nih.gov/12345678")
        
        assert result["metadata"]["source"] == "PubMed"
        assert result["metadata"]["title"] == "Test Medical Paper"
        assert "Dr. Smith" in result["metadata"]["authors"]
        assert result["metadata"]["journal"] == "Nature Medicine"
        assert result["metadata"]["doi"] == "10.1038/s41591-023-01234-5"
        assert "abstract of the medical paper" in result["content"]
    
    def test_general_academic_extraction(self):
        """Test general academic content extraction."""
        # Mock general academic HTML
        academic_html = """
        <html>
            <h1 class="title">Academic Paper Title</h1>
            <div class="authors">John Doe, Jane Smith</div>
            <div class="abstract">This is the paper abstract.</div>
        </html>
        """
        
        result = self.crawler._extract_general_academic(academic_html, "https://journal.example.com/paper")
        
        assert result["metadata"]["title"] == "Academic Paper Title"
        assert "John Doe" in result["metadata"]["authors"]
        assert "Jane Smith" in result["metadata"]["authors"]
        assert "This is the paper abstract" in result["content"]
        assert result["metadata"]["extraction_method"] == "general_academic"

class TestCrawlerManager:
    """Test the CrawlerManager class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.manager = CrawlerManager(max_workers=2)
    
    def teardown_method(self):
        """Clean up after tests."""
        self.manager.close()
    
    def test_crawler_selection(self):
        """Test that the manager selects appropriate crawlers."""
        # Test academic URL selection
        crawler = self.manager._select_crawler("https://arxiv.org/abs/2101.00001")
        assert isinstance(crawler, AcademicCrawler)
        
        # Test general web URL selection
        crawler = self.manager._select_crawler("https://example.com")
        assert isinstance(crawler, WebCrawler)
    
    def test_test_crawler_selection(self):
        """Test the test_crawler_selection method."""
        urls = [
            "https://arxiv.org/abs/2101.00001",
            "https://example.com",
            "https://pubmed.ncbi.nlm.nih.gov/12345"
        ]
        
        results = self.manager.test_crawler_selection(urls)
        
        assert results["https://arxiv.org/abs/2101.00001"] == "academic"
        assert results["https://example.com"] == "general_web"
        assert results["https://pubmed.ncbi.nlm.nih.gov/12345"] == "academic"
    
    @patch('src.crawlers.crawler_manager.CrawlerManager.crawl_url')
    def test_crawl_urls_concurrent(self, mock_crawl_url):
        """Test concurrent crawling of multiple URLs."""
        # Mock crawl results
        mock_crawl_url.side_effect = [
            CrawlResult("https://example1.com", success=True, content="Content 1"),
            CrawlResult("https://example2.com", success=True, content="Content 2"),
        ]
        
        urls = ["https://example1.com", "https://example2.com"]
        results = self.manager.crawl_urls(urls)
        
        assert len(results) == 2
        assert results[0].url == "https://example1.com"
        assert results[1].url == "https://example2.com"
        assert mock_crawl_url.call_count == 2
    
    def test_stats_tracking(self):
        """Test statistics tracking functionality."""
        # Reset stats
        self.manager.reset_stats()
        
        # Mock a successful crawl
        with patch.object(self.manager, '_select_crawler') as mock_select:
            mock_crawler = Mock()
            mock_crawler.crawl.return_value = CrawlResult(
                "https://example.com", success=True, content="Test"
            )
            mock_select.return_value = mock_crawler
            
            # Perform crawl
            result = self.manager.crawl_url("https://example.com")
            
            # Check stats
            stats = self.manager.get_stats()
            assert stats['total_crawls'] == 1
            assert stats['successful_crawls'] == 1
            assert stats['failed_crawls'] == 0
            assert stats['success_rate'] == 1.0
    
    def test_get_supported_domains(self):
        """Test getting supported domains."""
        domains = self.manager.get_supported_domains()
        
        assert isinstance(domains, list)
        assert len(domains) > 0
        # Should include academic domains and general web support
        assert any("arxiv.org" in str(domains) for domain in domains) or "*" in domains
    
    def test_add_remove_crawler(self):
        """Test adding and removing crawlers."""
        initial_count = len(self.manager.crawlers)
        
        # Add a custom crawler
        custom_crawler = Mock(spec=BaseCrawler)
        self.manager.add_crawler(custom_crawler)
        
        assert len(self.manager.crawlers) == initial_count + 1
        assert self.manager.crawlers[0] == custom_crawler  # Should be first (highest priority)
        
        # Remove the custom crawler
        self.manager.remove_crawler(type(custom_crawler))
        assert len(self.manager.crawlers) == initial_count
    
    def test_context_manager(self):
        """Test using CrawlerManager as a context manager."""
        with CrawlerManager() as manager:
            assert isinstance(manager, CrawlerManager)
            # Manager should be usable within context
            domains = manager.get_supported_domains()
            assert isinstance(domains, list)
        
        # After context, crawlers should be closed (we can't easily test this without mocking)

class TestCrawlerIntegration:
    """Integration tests for the crawler system."""
    
    def test_end_to_end_crawling_workflow(self):
        """Test the complete crawling workflow."""
        # This would be a real integration test, but we'll mock it for CI/CD
        with patch('requests.Session.get') as mock_get:
            # Mock a successful response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = """
            <html>
                <head><title>Test Article</title></head>
                <body>
                    <main>
                        <h1>Test Article Title</h1>
                        <p>This is the main content of the article.</p>
                    </main>
                </body>
            </html>
            """
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            # Test the workflow
            with CrawlerManager() as manager:
                result = manager.crawl_url("https://example.com/article")
                
                assert result.success is True
                assert "Test Article Title" in result.content or result.content != ""
                assert result.status_code == 200
                
                # Test stats
                stats = manager.get_stats()
                assert stats['total_crawls'] == 1
                assert stats['successful_crawls'] == 1

# Test data for parametrized tests
ACADEMIC_URLS = [
    "https://arxiv.org/abs/2101.00001",
    "https://pubmed.ncbi.nlm.nih.gov/12345678",
    "https://ieeexplore.ieee.org/document/12345",
    "https://dl.acm.org/doi/10.1145/12345.67890",
]

GENERAL_URLS = [
    "https://example.com",
    "https://news.example.com/article",
    "https://blog.example.com/post",
]

class TestParametrizedCrawling:
    """Parametrized tests for different URL types."""
    
    @pytest.mark.parametrize("url", ACADEMIC_URLS)
    def test_academic_crawler_selection(self, url):
        """Test that academic URLs are handled by AcademicCrawler."""
        with CrawlerManager() as manager:
            crawler = manager._select_crawler(url)
            assert isinstance(crawler, AcademicCrawler)
    
    @pytest.mark.parametrize("url", GENERAL_URLS)
    def test_web_crawler_selection(self, url):
        """Test that general URLs are handled by WebCrawler."""
        with CrawlerManager() as manager:
            crawler = manager._select_crawler(url)
            assert isinstance(crawler, WebCrawler)

# Performance tests
class TestCrawlerPerformance:
    """Performance tests for the crawler system."""
    
    def test_concurrent_crawling_performance(self):
        """Test that concurrent crawling is faster than sequential."""
        urls = ["https://example.com"] * 5
        
        with patch('requests.Session.get') as mock_get:
            # Mock response with small delay
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = "<html><body>Test</body></html>"
            mock_response.raise_for_status.return_value = None
            
            def mock_get_with_delay(*args, **kwargs):
                time.sleep(0.1)  # Simulate network delay
                return mock_response
            
            mock_get.side_effect = mock_get_with_delay
            
            with CrawlerManager(max_workers=3) as manager:
                start_time = time.time()
                results = manager.crawl_urls(urls)
                concurrent_time = time.time() - start_time
                
                # All should succeed
                assert all(r.success for r in results)
                assert len(results) == 5
                
                # Should be faster than sequential (5 * 0.1 = 0.5s)
                # With 3 workers, should take roughly 0.2s (2 batches)
                assert concurrent_time < 0.4  # Allow some overhead

if __name__ == "__main__":
    pytest.main([__file__])
