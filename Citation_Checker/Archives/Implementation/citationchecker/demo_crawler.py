#!/usr/bin/env python3
"""
Web Crawler Demo Script

This script demonstrates the web crawling functionality of the Citation Checker project.
It shows how to use the crawler system to extract content from various types of websites.
"""

import sys
import json
from typing import List

# Add the src directory to the path
sys.path.append('src')

from crawlers.crawler_manager import CrawlerManager
from crawlers.base_crawler import CrawlResult

def demo_basic_crawling():
    """Demonstrate basic web crawling functionality."""
    print("🕷️  Citation Checker - Web Crawler Demo")
    print("=" * 50)
    
    # Test URLs - mix of academic and general websites
    test_urls = [
        "https://arxiv.org/abs/2101.00001",  # arXiv paper
        "https://example.com",               # General website
        "https://httpbin.org/html",          # Test HTML endpoint
        "https://pubmed.ncbi.nlm.nih.gov/12345678",  # PubMed (will likely fail but shows handling)
    ]
    
    print(f"Testing crawler with {len(test_urls)} URLs:")
    for i, url in enumerate(test_urls, 1):
        print(f"  {i}. {url}")
    print()
    
    # Initialize crawler manager
    with CrawlerManager(max_workers=2, default_timeout=10) as manager:
        print("🔍 Testing crawler selection...")
        crawler_selection = manager.test_crawler_selection(test_urls)
        
        for url, crawler_name in crawler_selection.items():
            print(f"  {url[:50]}... → {crawler_name}")
        print()
        
        print("🌐 Starting crawling process...")
        results = manager.crawl_urls(test_urls)
        
        print(f"📊 Crawling completed! Results:")
        print("-" * 50)
        
        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result.url}")
            print(f"   Status: {'✅ Success' if result.success else '❌ Failed'}")
            
            if result.success:
                print(f"   Response Time: {result.response_time:.2f}s")
                print(f"   Status Code: {result.status_code}")
                print(f"   Content Length: {len(result.content)} characters")
                
                # Show metadata if available
                if result.metadata:
                    print(f"   Metadata:")
                    for key, value in result.metadata.items():
                        if key in ['title', 'extraction_method', 'source']:
                            print(f"     {key}: {str(value)[:100]}")
                
                # Show content preview
                content_preview = result.content[:200].replace('\n', ' ')
                print(f"   Content Preview: {content_preview}...")
            else:
                print(f"   Error: {result.error}")
        
        print("\n" + "=" * 50)
        print("📈 Crawling Statistics:")
        stats = manager.get_stats()
        
        print(f"   Total Crawls: {stats['total_crawls']}")
        print(f"   Successful: {stats['successful_crawls']}")
        print(f"   Failed: {stats['failed_crawls']}")
        print(f"   Success Rate: {stats['success_rate']:.1%}")
        print(f"   Average Time: {stats['avg_crawl_time']:.2f}s")
        
        if stats['crawler_usage']:
            print(f"   Crawler Usage:")
            for crawler, count in stats['crawler_usage'].items():
                print(f"     {crawler}: {count} URLs")

def demo_citation_integration():
    """Demonstrate integration with citation parsing."""
    print("\n" + "=" * 50)
    print("🔗 Citation Integration Demo")
    print("=" * 50)
    
    # Sample citations with URLs
    sample_citations = [
        {
            'authors': ['Smith, John'],
            'title': 'Example Paper',
            'url': 'https://example.com/paper1',
            'year': 2023
        },
        {
            'authors': ['Doe, Jane'],
            'title': 'Another Study',
            'url': 'https://httpbin.org/html',
            'year': 2023
        }
    ]
    
    print(f"Testing with {len(sample_citations)} sample citations:")
    for citation in sample_citations:
        print(f"  • {citation['authors'][0]} ({citation['year']}): {citation['title']}")
        print(f"    URL: {citation['url']}")
    print()
    
    with CrawlerManager() as manager:
        print("🔍 Crawling citation URLs...")
        results = manager.crawl_from_citations(sample_citations)
        
        print(f"📊 Results:")
        for i, result in enumerate(results):
            citation = sample_citations[i]
            print(f"\n{i+1}. {citation['title']}")
            print(f"   URL: {result.url}")
            print(f"   Status: {'✅ Success' if result.success else '❌ Failed'}")
            
            if result.success:
                print(f"   Content extracted: {len(result.content)} characters")
                # This is where you would integrate with verification logic
                print(f"   Ready for verification: ✅")
            else:
                print(f"   Error: {result.error}")
                print(f"   Verification status: ❌ Cannot verify")

def demo_supported_domains():
    """Show supported domains and crawler capabilities."""
    print("\n" + "=" * 50)
    print("🌍 Supported Domains")
    print("=" * 50)
    
    with CrawlerManager() as manager:
        domains = manager.get_supported_domains()
        
        print("The crawler system supports the following domains:")
        
        academic_domains = [d for d in domains if d != "*"]
        general_support = "*" in domains
        
        if academic_domains:
            print("\n📚 Academic Domains:")
            for domain in sorted(academic_domains):
                print(f"  • {domain}")
        
        if general_support:
            print("\n🌐 General Web Support:")
            print("  • All HTTP/HTTPS websites (with fallback extraction)")
        
        print(f"\nTotal: {len(academic_domains)} specialized academic domains + general web support")

def main():
    """Main demo function."""
    try:
        demo_basic_crawling()
        demo_citation_integration()
        demo_supported_domains()
        
        print("\n" + "=" * 50)
        print("✅ Demo completed successfully!")
        print("The web crawler is ready for integration with the citation verification system.")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Demo interrupted by user.")
    except Exception as e:
        print(f"\n❌ Demo failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
