"""
Test script for LinkedIn Company Scraper
Run from Command Prompt: python test_scraper.py
"""

import asyncio
import logging
import os
from app.services.scraper import LinkedInScraper

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_scraper():
    """Test the LinkedIn scraper"""
    
    # Get credentials from environment or hardcode for testing
    email = os.getenv('LINKEDIN_EMAIL', 'your@gmail.com')
    password = os.getenv('LINKEDIN_PASSWORD',"your_password")
    
    logger.info("=" * 80)
    logger.info("Starting LinkedIn Scraper Test")
    logger.info("=" * 80)
    
    scraper = None
    
    try:
        # Initialize scraper (headless=False to see browser)
        logger.info("Initializing scraper...")
        scraper = LinkedInScraper(
            email=email,
            password=password,
            headless=False  # Set to True after first successful run
        )
        
        logger.info("✅ Scraper initialized successfully")
        
        # Test with Microsoft
        logger.info("\n" + "=" * 80)
        logger.info("Testing with: Microsoft Corporation")
        logger.info("=" * 80)
        
        result = await scraper.scrape_page("Microsoft Corporation")
        
        # Print results
        print("\n" + "=" * 80)
        print("SCRAPING RESULTS")
        print("=" * 80)
        print(f"Company Name: {result.get('name', 'N/A')}")

        desc = result.get('description')
        if desc:
            print(f"Description: {desc[:100]}...")
        else:
            print(f"Description: N/A")

        print(f"Industry: {result.get('industry', 'N/A')}")
        print(f"Followers: {result.get('followers_count', 0)}")
        print(f"Website: {result.get('website', 'N/A')}")
        print(f"\nPosts found: {len(result.get('posts', []))}")
        print(f"Employees found: {len(result.get('employees', []))}")

        # Print first post
        if result.get('posts'):
            print("\n--- First Post ---")
            post = result['posts'][0]
            content = post.get('content', 'N/A')
            print(f"Content: {content[:150] if content else 'N/A'}...")
            print(f"Likes: {post.get('likes_count', 0)}")
            print(f"Comments: {post.get('comments_count', 0)}")

        # Print first employee
        if result.get('employees'):
            print("\n--- First Employee ---")
            emp = result['employees'][0]
            print(f"Name: {emp.get('name', 'N/A')}")
            print(f"Headline: {emp.get('headline', 'N/A')}")
            print(f"Profile: {emp.get('profile_url', 'N/A')}")

        print("\n" + "=" * 80)
        print("✅ TEST COMPLETED SUCCESSFULLY")
        print(f"✅ Got {len(result.get('posts', []))} posts and {len(result.get('employees', []))} employees")
        print("=" * 80)
        
        print("\n" + "=" * 80)
        print("✅ TEST COMPLETED SUCCESSFULLY")
        print("=" * 80)
        
        # Show debug files location
        print("\nDebug HTML files saved:")
        print(f"  - debug_microsoft-corporation_posts.html")
        print(f"  - debug_microsoft-corporation_people.html")
        print("\nOpen these files in a browser to see what was scraped.")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {str(e)}", exc_info=True)
        print("\n" + "=" * 80)
        print("❌ TEST FAILED")
        print("=" * 80)
        print(f"Error: {str(e)}")
        
        # Provide troubleshooting tips
        print("\n🔧 TROUBLESHOOTING:")
        print("1. Make sure Chrome is installed")
        print("2. Check your LinkedIn credentials")
        print("3. If you see a verification challenge, complete it in the browser")
        print("4. After first successful login, cookies will be saved")
        print("5. Check the console output for specific errors")
        
    finally:
        if scraper:
            scraper.close()
            logger.info("Browser closed")

if __name__ == "__main__":
    # For Windows Command Prompt
    print("\n" + "=" * 80)
    print("LinkedIn Company Scraper - Test Script")
    print("=" * 80)
    print("\nMake sure you have:")
    print("  1. Chrome installed")
    print("  2. Set environment variables (or edit this script):")
    print("     set LINKEDIN_EMAIL=your_email@example.com")
    print("     set LINKEDIN_PASSWORD=your_password")
    print("\n" + "=" * 80 + "\n")
    
    # Run the async function
    asyncio.run(test_scraper())