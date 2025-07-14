"""
Web Crawling Module for Citation Checker

This module provides web crawling functionality to retrieve and extract content
from online sources referenced in citations.
"""

from .base_crawler import BaseCrawler
from .crawler_manager import CrawlerManager
from .web_crawler import WebCrawler
from .academic_crawler import AcademicCrawler

__all__ = [
    'BaseCrawler',
    'CrawlerManager', 
    'WebCrawler',
    'AcademicCrawler'
]
