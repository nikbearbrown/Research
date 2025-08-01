"""
Academic Crawler

This module implements a specialized crawler for academic websites and repositories
such as arXiv, PubMed, IEEE Xplore, ACM Digital Library, and others.
"""

import re
from typing import Dict, Any, List
from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup

from .base_crawler import BaseCrawler

class AcademicCrawler(BaseCrawler):
    """Specialized crawler for academic websites and repositories.
    
    This crawler knows how to extract content from major academic platforms
    and can handle their specific HTML structures and metadata formats.
    """
    
    def __init__(self, **kwargs):
        """Initialize the academic crawler."""
        super().__init__(**kwargs)
        self.name = "academic"
        
        # Define academic domains and their extraction strategies
        self.academic_domains = {
            'arxiv.org': self._extract_arxiv,
            'pubmed.ncbi.nlm.nih.gov': self._extract_pubmed,
            'ieeexplore.ieee.org': self._extract_ieee,
            'dl.acm.org': self._extract_acm,
            'scholar.google.com': self._extract_google_scholar,
            'jstor.org': self._extract_jstor,
            'springer.com': self._extract_springer,
            'sciencedirect.com': self._extract_sciencedirect,
            'nature.com': self._extract_nature,
            'science.org': self._extract_science,
            'plos.org': self._extract_plos,
            'biorxiv.org': self._extract_biorxiv,
            'medrxiv.org': self._extract_medrxiv,
        }
    
    def can_crawl(self, url: str) -> bool:
        """Check if this crawler can handle the given URL.
        
        Args:
            url: The URL to check
            
        Returns:
            True if the URL is from a known academic domain, False otherwise
        """
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # Check exact matches and subdomain matches
            for academic_domain in self.academic_domains.keys():
                if domain == academic_domain or domain.endswith('.' + academic_domain):
                    return True
            
            return False
        except:
            return False
    
    def extract_content(self, html: str, url: str) -> Dict[str, Any]:
        """Extract structured content from academic websites.
        
        Args:
            html: Raw HTML content
            url: The URL the content was retrieved from
            
        Returns:
            Dictionary containing extracted content and metadata
        """
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.lower()
        
        # Find the appropriate extraction method
        extraction_method = None
        for academic_domain, method in self.academic_domains.items():
            if domain == academic_domain or domain.endswith('.' + academic_domain):
                extraction_method = method
                break
        
        if extraction_method:
            try:
                return extraction_method(html, url)
            except Exception as e:
                # Fall back to general academic extraction
                return self._extract_general_academic(html, url)
        else:
            # Fall back to general academic extraction
            return self._extract_general_academic(html, url)
    
    def _extract_arxiv(self, html: str, url: str) -> Dict[str, Any]:
        """Extract content from arXiv papers.
        
        Args:
            html: HTML content
            url: Source URL
            
        Returns:
            Dictionary containing extracted content and metadata
        """
        soup = BeautifulSoup(html, 'html.parser')
        metadata = self._extract_metadata_from_html(html, url)
        
        # Extract arXiv-specific metadata
        metadata['source'] = 'arXiv'
        
        # Extract arXiv ID from URL
        arxiv_id_match = re.search(r'arxiv\.org/abs/(\d+\.\d+)', url)
        if arxiv_id_match:
            metadata['arxiv_id'] = arxiv_id_match.group(1)
        
        # Extract title
        title_elem = soup.find('h1', class_='title')
        if title_elem:
            title = title_elem.get_text().replace('Title:', '').strip()
            metadata['title'] = title
        
        # Extract authors
        authors_elem = soup.find('div', class_='authors')
        if authors_elem:
            authors = []
            for author_link in authors_elem.find_all('a'):
                authors.append(author_link.get_text().strip())
            metadata['authors'] = authors
        
        # Extract abstract
        abstract_elem = soup.find('blockquote', class_='abstract')
        if abstract_elem:
            abstract = abstract_elem.get_text().replace('Abstract:', '').strip()
            content = f"Title: {metadata.get('title', '')}\n\nAbstract: {abstract}"
        else:
            content = f"Title: {metadata.get('title', '')}"
        
        # Extract submission date
        dateline = soup.find('div', class_='dateline')
        if dateline:
            date_text = dateline.get_text()
            date_match = re.search(r'\(Submitted on (.+?)\)', date_text)
            if date_match:
                metadata['submission_date'] = date_match.group(1)
        
        # Extract subjects
        subjects_elem = soup.find('td', class_='tablecell subjects')
        if subjects_elem:
            subjects = [s.strip() for s in subjects_elem.get_text().split(';')]
            metadata['subjects'] = subjects
        
        metadata['extraction_method'] = 'arxiv_specific'
        return {'content': content, 'metadata': metadata}
    
    def _extract_pubmed(self, html: str, url: str) -> Dict[str, Any]:
        """Extract content from PubMed articles.
        
        Args:
            html: HTML content
            url: Source URL
            
        Returns:
            Dictionary containing extracted content and metadata
        """
        soup = BeautifulSoup(html, 'html.parser')
        metadata = self._extract_metadata_from_html(html, url)
        metadata['source'] = 'PubMed'
        
        # Extract PMID
        pmid_match = re.search(r'pubmed/(\d+)', url)
        if pmid_match:
            metadata['pmid'] = pmid_match.group(1)
        
        # Extract title
        title_elem = soup.find('h1', class_='heading-title')
        if title_elem:
            metadata['title'] = title_elem.get_text().strip()
        
        # Extract authors
        authors_elem = soup.find('div', class_='authors-list')
        if authors_elem:
            authors = []
            for author in authors_elem.find_all('a', class_='full-name'):
                authors.append(author.get_text().strip())
            metadata['authors'] = authors
        
        # Extract abstract
        abstract_elem = soup.find('div', class_='abstract-content')
        if abstract_elem:
            abstract = abstract_elem.get_text().strip()
            content = f"Title: {metadata.get('title', '')}\n\nAbstract: {abstract}"
        else:
            content = f"Title: {metadata.get('title', '')}"
        
        # Extract journal information
        journal_elem = soup.find('button', id='full-view-journal-trigger')
        if journal_elem:
            metadata['journal'] = journal_elem.get_text().strip()
        
        # Extract DOI
        doi_elem = soup.find('span', class_='citation-doi')
        if doi_elem:
            doi_text = doi_elem.get_text()
            doi_match = re.search(r'doi:\s*(.+)', doi_text)
            if doi_match:
                metadata['doi'] = doi_match.group(1).strip()
        
        metadata['extraction_method'] = 'pubmed_specific'
        return {'content': content, 'metadata': metadata}
    
    def _extract_ieee(self, html: str, url: str) -> Dict[str, Any]:
        """Extract content from IEEE Xplore.
        
        Args:
            html: HTML content
            url: Source URL
            
        Returns:
            Dictionary containing extracted content and metadata
        """
        soup = BeautifulSoup(html, 'html.parser')
        metadata = self._extract_metadata_from_html(html, url)
        metadata['source'] = 'IEEE Xplore'
        
        # Extract title
        title_elem = soup.find('h1', class_='document-title')
        if title_elem:
            metadata['title'] = title_elem.get_text().strip()
        
        # Extract authors
        authors_section = soup.find('div', class_='authors-info')
        if authors_section:
            authors = []
            for author in authors_section.find_all('span', class_='author-name'):
                authors.append(author.get_text().strip())
            metadata['authors'] = authors
        
        # Extract abstract
        abstract_elem = soup.find('div', class_='abstract-text')
        if abstract_elem:
            abstract = abstract_elem.get_text().strip()
            content = f"Title: {metadata.get('title', '')}\n\nAbstract: {abstract}"
        else:
            content = f"Title: {metadata.get('title', '')}"
        
        # Extract publication info
        pub_info = soup.find('div', class_='publication-data')
        if pub_info:
            metadata['publication_info'] = pub_info.get_text().strip()
        
        metadata['extraction_method'] = 'ieee_specific'
        return {'content': content, 'metadata': metadata}
    
    def _extract_acm(self, html: str, url: str) -> Dict[str, Any]:
        """Extract content from ACM Digital Library.
        
        Args:
            html: HTML content
            url: Source URL
            
        Returns:
            Dictionary containing extracted content and metadata
        """
        soup = BeautifulSoup(html, 'html.parser')
        metadata = self._extract_metadata_from_html(html, url)
        metadata['source'] = 'ACM Digital Library'
        
        # Extract title
        title_elem = soup.find('h1', class_='citation__title')
        if title_elem:
            metadata['title'] = title_elem.get_text().strip()
        
        # Extract authors
        authors_section = soup.find('div', class_='loa__author-info')
        if authors_section:
            authors = []
            for author in authors_section.find_all('a', class_='author-name'):
                authors.append(author.get_text().strip())
            metadata['authors'] = authors
        
        # Extract abstract
        abstract_elem = soup.find('div', class_='abstractSection')
        if abstract_elem:
            abstract = abstract_elem.get_text().strip()
            content = f"Title: {metadata.get('title', '')}\n\nAbstract: {abstract}"
        else:
            content = f"Title: {metadata.get('title', '')}"
        
        metadata['extraction_method'] = 'acm_specific'
        return {'content': content, 'metadata': metadata}
    
    def _extract_google_scholar(self, html: str, url: str) -> Dict[str, Any]:
        """Extract content from Google Scholar.
        
        Args:
            html: HTML content
            url: Source URL
            
        Returns:
            Dictionary containing extracted content and metadata
        """
        soup = BeautifulSoup(html, 'html.parser')
        metadata = self._extract_metadata_from_html(html, url)
        metadata['source'] = 'Google Scholar'
        
        # Google Scholar has limited content extraction due to dynamic loading
        # Extract what we can from the static HTML
        
        # Extract title from search results or paper view
        title_elem = soup.find('h3', class_='gs_rt') or soup.find('a', class_='gs_rt')
        if title_elem:
            metadata['title'] = title_elem.get_text().strip()
        
        # Extract snippet/abstract
        snippet_elem = soup.find('div', class_='gs_rs')
        if snippet_elem:
            content = f"Title: {metadata.get('title', '')}\n\nSnippet: {snippet_elem.get_text().strip()}"
        else:
            content = f"Title: {metadata.get('title', '')}"
        
        metadata['extraction_method'] = 'google_scholar_specific'
        return {'content': content, 'metadata': metadata}
    
    def _extract_jstor(self, html: str, url: str) -> Dict[str, Any]:
        """Extract content from JSTOR.
        
        Args:
            html: HTML content
            url: Source URL
            
        Returns:
            Dictionary containing extracted content and metadata
        """
        return self._extract_general_academic(html, url, source='JSTOR')
    
    def _extract_springer(self, html: str, url: str) -> Dict[str, Any]:
        """Extract content from Springer.
        
        Args:
            html: HTML content
            url: Source URL
            
        Returns:
            Dictionary containing extracted content and metadata
        """
        return self._extract_general_academic(html, url, source='Springer')
    
    def _extract_sciencedirect(self, html: str, url: str) -> Dict[str, Any]:
        """Extract content from ScienceDirect.
        
        Args:
            html: HTML content
            url: Source URL
            
        Returns:
            Dictionary containing extracted content and metadata
        """
        return self._extract_general_academic(html, url, source='ScienceDirect')
    
    def _extract_nature(self, html: str, url: str) -> Dict[str, Any]:
        """Extract content from Nature.
        
        Args:
            html: HTML content
            url: Source URL
            
        Returns:
            Dictionary containing extracted content and metadata
        """
        return self._extract_general_academic(html, url, source='Nature')
    
    def _extract_science(self, html: str, url: str) -> Dict[str, Any]:
        """Extract content from Science.
        
        Args:
            html: HTML content
            url: Source URL
            
        Returns:
            Dictionary containing extracted content and metadata
        """
        return self._extract_general_academic(html, url, source='Science')
    
    def _extract_plos(self, html: str, url: str) -> Dict[str, Any]:
        """Extract content from PLOS.
        
        Args:
            html: HTML content
            url: Source URL
            
        Returns:
            Dictionary containing extracted content and metadata
        """
        return self._extract_general_academic(html, url, source='PLOS')
    
    def _extract_biorxiv(self, html: str, url: str) -> Dict[str, Any]:
        """Extract content from bioRxiv.
        
        Args:
            html: HTML content
            url: Source URL
            
        Returns:
            Dictionary containing extracted content and metadata
        """
        return self._extract_general_academic(html, url, source='bioRxiv')
    
    def _extract_medrxiv(self, html: str, url: str) -> Dict[str, Any]:
        """Extract content from medRxiv.
        
        Args:
            html: HTML content
            url: Source URL
            
        Returns:
            Dictionary containing extracted content and metadata
        """
        return self._extract_general_academic(html, url, source='medRxiv')
    
    def _extract_general_academic(self, html: str, url: str, source: str = None) -> Dict[str, Any]:
        """General academic content extraction for sites without specific handlers.
        
        Args:
            html: HTML content
            url: Source URL
            source: Optional source name
            
        Returns:
            Dictionary containing extracted content and metadata
        """
        soup = BeautifulSoup(html, 'html.parser')
        metadata = self._extract_metadata_from_html(html, url)
        
        if source:
            metadata['source'] = source
        
        # Look for common academic paper elements
        content_parts = []
        
        # Extract title
        title_selectors = [
            'h1.title', 'h1.article-title', 'h1.paper-title',
            '.title', '.article-title', '.paper-title',
            'h1', 'title'
        ]
        
        title = None
        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem and len(title_elem.get_text().strip()) > 5:
                title = self._clean_text(title_elem.get_text())
                metadata['title'] = title
                content_parts.append(f"Title: {title}")
                break
        
        # Extract authors
        author_selectors = [
            '.authors', '.author-list', '.author-names',
            '.byline', '.contributors'
        ]
        
        for selector in author_selectors:
            authors_elem = soup.select_one(selector)
            if authors_elem:
                authors_text = authors_elem.get_text()
                # Simple author extraction - could be improved
                authors = [a.strip() for a in re.split(r'[,;]|and', authors_text) if a.strip()]
                if authors:
                    metadata['authors'] = authors[:10]  # Limit to 10 authors
                    break
        
        # Extract abstract
        abstract_selectors = [
            '.abstract', '.summary', '.description',
            '#abstract', '#summary', '#description'
        ]
        
        for selector in abstract_selectors:
            abstract_elem = soup.select_one(selector)
            if abstract_elem:
                abstract_text = self._clean_text(abstract_elem.get_text())
                if len(abstract_text) > 50:  # Ensure it's substantial
                    content_parts.append(f"Abstract: {abstract_text}")
                    break
        
        # Extract DOI
        doi_patterns = [
            r'doi:\s*([^\s]+)',
            r'DOI:\s*([^\s]+)',
            r'https?://doi\.org/([^\s]+)'
        ]
        
        for pattern in doi_patterns:
            doi_match = re.search(pattern, html, re.IGNORECASE)
            if doi_match:
                metadata['doi'] = doi_match.group(1)
                break
        
        # Combine content
        content = '\n\n'.join(content_parts) if content_parts else title or "No content extracted"
        
        metadata['extraction_method'] = 'general_academic'
        return {'content': content, 'metadata': metadata}
