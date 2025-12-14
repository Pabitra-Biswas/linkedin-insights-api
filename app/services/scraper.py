# import asyncio
# import time
# import pickle
# import os
# from typing import Dict, List, Optional
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException, NoSuchElementException
# from bs4 import BeautifulSoup
# import undetected_chromedriver as uc
# from app.config import settings
# import logging

# logger = logging.getLogger(__name__)

# class LinkedInScraper:
#     def __init__(self, email=None, password=None):
#         self.driver = None
#         self.email = email or settings.LINKEDIN_EMAIL
#         self.password = password or settings.LINKEDIN_PASSWORD
#         self.cookies_file = "linkedin_cookies.pkl"
#         self.setup_driver()
        
#         # Try cookies first, then login
#         if os.path.exists(self.cookies_file):
#             self.load_cookies()
#             if not self.verify_login():
#                 logger.warning("⚠️ Saved cookies invalid, logging in fresh")
#                 if self.email and self.password:
#                     self.login()
#                     self.save_cookies()
#         elif self.email and self.password:
#             self.login()
#             self.save_cookies()
    
#     def setup_driver(self):
#         """Initialize undetected Chrome driver"""
#         options = uc.ChromeOptions()
        
#         options.add_argument('--no-sandbox')
#         options.add_argument('--disable-dev-shm-usage')
#         options.add_argument('--disable-blink-features=AutomationControlled')
#         options.add_argument('--window-size=1920,1080')
#         options.add_argument('--start-maximized')
#         options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
#         try:
#             self.driver = uc.Chrome(options=options)
#         except Exception as e:
#             logger.warning(f"⚠️ Failed with options: {e}")
#             self.driver = uc.Chrome(use_subprocess=True)
        
#         try:
#             self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
#         except:
#             pass
        
#         logger.info("✅ Selenium driver initialized")
    
#     def save_cookies(self):
#         """Save cookies for reuse"""
#         try:
#             cookies = self.driver.get_cookies()
#             with open(self.cookies_file, 'wb') as f:
#                 pickle.dump(cookies, f)
#             logger.info("✅ Saved cookies")
#         except Exception as e:
#             logger.error(f"❌ Failed to save cookies: {e}")
    
#     def load_cookies(self):
#         """Load saved cookies"""
#         try:
#             self.driver.get("https://www.linkedin.com")
#             time.sleep(2)
            
#             with open(self.cookies_file, 'rb') as f:
#                 cookies = pickle.load(f)
            
#             for cookie in cookies:
#                 try:
#                     self.driver.add_cookie(cookie)
#                 except:
#                     pass
            
#             self.driver.refresh()
#             time.sleep(2)
#             logger.info("✅ Loaded cookies")
#         except Exception as e:
#             logger.error(f"❌ Failed to load cookies: {e}")
    
#     def verify_login(self) -> bool:
#         """Check if currently logged in"""
#         try:
#             self.driver.get("https://www.linkedin.com/feed")
#             time.sleep(3)
            
#             if "feed" in self.driver.current_url:
#                 logger.info("✅ Login verified")
#                 return True
#             else:
#                 logger.warning("⚠️ Not logged in")
#                 return False
#         except:
#             return False
    
#     def login(self):
#         """Login to LinkedIn"""
#         try:
#             logger.info("🔐 Logging into LinkedIn...")
#             self.driver.get("https://www.linkedin.com/login")
#             time.sleep(3)
            
#             if "feed" in self.driver.current_url:
#                 logger.info("✅ Already logged in!")
#                 return
            
#             email_field = self.driver.find_element(By.ID, "username")
#             email_field.clear()
#             email_field.send_keys(self.email)
#             time.sleep(1)
            
#             password_field = self.driver.find_element(By.ID, "password")
#             password_field.clear()
#             password_field.send_keys(self.password)
#             time.sleep(1)
            
#             login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
#             login_button.click()
            
#             time.sleep(8)
            
#             current_url = self.driver.current_url
#             logger.info(f"📍 URL after login: {current_url}")
            
#             if "feed" in current_url or "checkpoint" in current_url:
#                 logger.info("✅ Successfully logged in")
#             elif "authwall" in current_url or "login" in current_url:
#                 logger.error("❌ Login failed")
#                 raise Exception("LinkedIn login failed")
            
#         except Exception as e:
#             logger.error(f"❌ Login failed: {str(e)}")
#             raise
    
#     def close(self):
#         """Close driver"""
#         if self.driver:
#             self.driver.quit()
#             logger.info("❌ Driver closed")
    
#     async def scrape_page(self, page_id: str) -> Dict:
#         """Main scraping with auth wall detection"""
#         try:
#             logger.info(f"🔍 Starting scrape: {page_id}")
            
#             url = f"https://www.linkedin.com/company/{page_id}/"
#             self.driver.get(url)
#             await asyncio.sleep(5)
            
#             # Check for auth wall
#             if "authwall" in self.driver.current_url or "auth_wall" in self.driver.page_source:
#                 logger.error("🚫 Hit auth wall!")
#                 logger.info("🔄 Re-logging in...")
#                 self.login()
#                 self.save_cookies()
                
#                 self.driver.get(url)
#                 await asyncio.sleep(5)
                
#                 if "authwall" in self.driver.current_url:
#                     raise Exception("Failed to bypass auth wall")
            
#             if "Page not found" in self.driver.page_source or "404" in self.driver.title:
#                 raise ValueError(f"Page '{page_id}' not found")
            
#             basic_info = await self._scrape_basic_info(page_id)
#             posts = await self._scrape_posts(page_id, limit=20)
#             employees = await self._scrape_employees(page_id, limit=50)
            
#             result = {
#                 **basic_info,
#                 "posts": posts,
#                 "employees": employees
#             }
            
#             logger.info(f"✅ Successfully scraped: {page_id}")
#             return result
            
#         except Exception as e:
#             logger.error(f"❌ Scraping failed: {str(e)}")
#             raise
    
#     # Keep all your existing _scrape_basic_info, _scrape_posts, _scrape_employees methods
#     # ... (same as before)
    
#     async def _scrape_basic_info(self, page_id: str) -> Dict:
#         """Extract basic page information"""
#         soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        
#         data = {
#             "page_id": page_id,
#             "url": self.driver.current_url
#         }
        
#         try:
#             # Page Name - Try multiple selectors
#             name_elem = soup.select_one('h1.org-top-card-summary__title')
#             if not name_elem:
#                 name_elem = soup.select_one('h1.org-top-card-summary-info-list__title')
#             data['name'] = name_elem.text.strip() if name_elem else page_id
            
#             # LinkedIn ID
#             data['linkedin_id'] = self._extract_linkedin_id()
            
#             # Profile Picture
#             img_elem = soup.select_one('img.org-top-card-primary-content__logo')
#             if not img_elem:
#                 img_elem = soup.select_one('img[alt*="logo"]')
#             data['profile_picture'] = img_elem.get('src') if img_elem else None
            
#             # Description/Tagline
#             desc_elem = soup.select_one('p.org-top-card-summary__tagline')
#             if not desc_elem:
#                 desc_elem = soup.select_one('p.break-words')
#             data['description'] = desc_elem.text.strip() if desc_elem else None
            
#             # Website
#             website_elem = soup.select_one('a.link-without-visited-state[href*="http"]')
#             if not website_elem:
#                 website_elem = soup.select_one('a[data-tracking-control-name*="website"]')
#             data['website'] = website_elem.get('href') if website_elem else None
            
#             # Industry - Improved selector
#             industry_text = None
#             info_items = soup.select('div.org-top-card-summary-info-list__info-item')
#             for item in info_items:
#                 if 'Industry' in item.text or 'industry' in item.text.lower():
#                     industry_text = item.text.replace('Industry', '').strip()
#                     break
#             data['industry'] = industry_text
            
#             # Followers
#             followers_text = None
#             for item in info_items:
#                 if 'follower' in item.text.lower():
#                     followers_text = item.text
#                     break
#             data['followers_count'] = self._parse_count(followers_text if followers_text else "0")
            
#             # Head Count
#             headcount_text = None
#             for item in info_items:
#                 if 'employee' in item.text.lower():
#                     headcount_text = item.text.strip()
#                     break
#             data['head_count'] = headcount_text
            
#             # Specialities
#             specialities = []
#             spec_section = soup.select('dd.org-page-details__definition-text')
#             for spec in spec_section:
#                 items = spec.text.strip().split(',')
#                 specialities.extend([s.strip() for s in items])
#             data['specialities'] = specialities[:10]
            
#             logger.info(f"✅ Basic info scraped for {page_id}")
#             return data
            
#         except Exception as e:
#             logger.error(f"❌ Error scraping basic info: {str(e)}")
#             return data
    
#     async def _scrape_posts(self, page_id: str, limit: int = 20) -> List[Dict]:
#         """Scrape recent posts from the page"""
#         posts = []
        
#         try:
#             posts_url = f"https://www.linkedin.com/company/{page_id}/posts/"
#             logger.info(f"📝 Navigating to: {posts_url}")
#             self.driver.get(posts_url)
            
#             await asyncio.sleep(5)
            
#             # Wait for posts
#             try:
#                 wait = WebDriverWait(self.driver, 10)
#                 wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.scaffold-finite-scroll__content")))
#                 logger.info("✅ Posts container found")
#             except TimeoutException:
#                 logger.warning("⚠️ Posts container not found")
            
#             # Scroll
#             for i in range(5):
#                 self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#                 await asyncio.sleep(2)
#                 logger.info(f"📜 Scroll {i+1}/5")
            
#             # Save debug
#             with open(f"debug_{page_id}_posts.html", "w", encoding="utf-8") as f:
#                 f.write(self.driver.page_source)
#             logger.info(f"💾 Saved debug HTML to debug_{page_id}_posts.html")
            
#             soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
#             # Try multiple selectors
#             post_elements = soup.select('div.feed-shared-update-v2')
#             if not post_elements:
#                 post_elements = soup.select('div[data-urn*="activity"]')
#             if not post_elements:
#                 post_elements = soup.select('article.feed-shared-update-v2')
            
#             logger.info(f"📝 Found {len(post_elements)} post elements")
            
#             for idx, post_elem in enumerate(post_elements[:limit]):
#                 try:
#                     post_data = {
#                         "post_id": f"{page_id}_post_{idx}_{int(time.time())}",
#                         "page_id": page_id,
#                         "content": "",
#                         "likes_count": 0,
#                         "comments_count": 0,
#                         "shares_count": 0,
#                         "media_urls": [],
#                         "comments": []
#                     }
                    
#                     # Post content
#                     content_elem = post_elem.select_one('div.feed-shared-text')
#                     if not content_elem:
#                         content_elem = post_elem.select_one('div.feed-shared-update-v2__description-wrapper')
#                     if not content_elem:
#                         content_elem = post_elem.select_one('span.break-words')
                    
#                     if content_elem:
#                         post_data['content'] = content_elem.text.strip()
                    
#                     # Engagement
#                     likes_elem = post_elem.select_one('span.social-details-social-counts__reactions-count')
#                     if likes_elem:
#                         post_data['likes_count'] = self._parse_count(likes_elem.text)
                    
#                     comments_elem = post_elem.select_one('button[aria-label*="comment"]')
#                     if not comments_elem:
#                         comments_elem = post_elem.select_one('span.social-details-social-counts__comments')
#                     if comments_elem:
#                         post_data['comments_count'] = self._parse_count(comments_elem.text)
                    
#                     # Media
#                     media_elems = post_elem.select('img.feed-shared-image__image')
#                     if not media_elems:
#                         media_elems = post_elem.select('img.ivm-view-attr__img--centered')
#                     post_data['media_urls'] = [img.get('src') for img in media_elems if img.get('src')]
                    
#                     posts.append(post_data)
#                     logger.info(f"✅ Parsed post {idx+1}")
                    
#                 except Exception as e:
#                     logger.warning(f"⚠️ Failed to parse post {idx}: {str(e)}")
#                     continue
            
#             logger.info(f"✅ Scraped {len(posts)} posts for {page_id}")
#             return posts
            
#         except Exception as e:
#             logger.error(f"❌ Error scraping posts: {str(e)}")
#             return posts
    
#     async def _scrape_employees(self, page_id: str, limit: int = 50) -> List[Dict]:
#         """Scrape employees"""
#         employees = []
        
#         try:
#             people_url = f"https://www.linkedin.com/company/{page_id}/people/"
#             logger.info(f"👥 Navigating to: {people_url}")
#             self.driver.get(people_url)
            
#             await asyncio.sleep(5)
            
#             # Wait for grid
#             try:
#                 wait = WebDriverWait(self.driver, 10)
#                 wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "ul.scaffold-finite-scroll__content")))
#                 logger.info("✅ People grid found")
#             except TimeoutException:
#                 logger.warning("⚠️ People grid not found")
            
#             # Scroll
#             for i in range(3):
#                 self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#                 await asyncio.sleep(2)
#                 logger.info(f"📜 Scroll {i+1}/3")
            
#             # Save debug
#             with open(f"debug_{page_id}_people.html", "w", encoding="utf-8") as f:
#                 f.write(self.driver.page_source)
#             logger.info(f"💾 Saved debug HTML to debug_{page_id}_people.html")
            
#             soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
#             # Try multiple selectors
#             people_elements = soup.select('li.org-people-profile-card__profile-card-spacing')
#             if not people_elements:
#                 people_elements = soup.select('div.org-people-profile-card')
#             if not people_elements:
#                 people_elements = soup.select('li.artdeco-list__item')
            
#             logger.info(f"👥 Found {len(people_elements)} people elements")
            
#             for idx, person_elem in enumerate(people_elements[:limit]):
#                 try:
#                     employee_data = {
#                         "user_id": f"{page_id}_user_{idx}_{int(time.time())}",
#                         "name": "",
#                         "profile_url": "",
#                         "profile_picture": None,
#                         "headline": None,
#                         "current_company": page_id
#                     }
                    
#                     # Name
#                     name_elem = person_elem.select_one('span.org-people-profile-card__profile-title')
#                     if not name_elem:
#                         name_elem = person_elem.select_one('div.artdeco-entity-lockup__title')
#                     if name_elem:
#                         employee_data['name'] = name_elem.text.strip()
                    
#                     # Profile URL
#                     link_elem = person_elem.select_one('a.app-aware-link')
#                     if not link_elem:
#                         link_elem = person_elem.select_one('a[href*="/in/"]')
#                     if link_elem:
#                         employee_data['profile_url'] = link_elem.get('href', '')
                    
#                     # Picture
#                     img_elem = person_elem.select_one('img')
#                     if img_elem:
#                         employee_data['profile_picture'] = img_elem.get('src')
                    
#                     # Headline
#                     headline_elem = person_elem.select_one('div.artdeco-entity-lockup__subtitle')
#                     if not headline_elem:
#                         headline_elem = person_elem.select_one('span.artdeco-entity-lockup__subtitle')
#                     if headline_elem:
#                         employee_data['headline'] = headline_elem.text.strip()
                    
#                     if employee_data['name']:
#                         employees.append(employee_data)
#                         logger.info(f"✅ Parsed employee {idx+1}")
                    
#                 except Exception as e:
#                     logger.warning(f"⚠️ Failed to parse employee {idx}: {str(e)}")
#                     continue
            
#             logger.info(f"✅ Scraped {len(employees)} employees for {page_id}")
#             return employees
            
#         except Exception as e:
#             logger.error(f"❌ Error scraping employees: {str(e)}")
#             return employees
    
#     def _extract_linkedin_id(self) -> Optional[str]:
#         """Extract LinkedIn platform ID"""
#         try:
#             page_source = self.driver.page_source
#             if 'organizationId' in page_source:
#                 import re
#                 match = re.search(r'"organizationId":"(\d+)"', page_source)
#                 if match:
#                     return match.group(1)
#         except:
#             pass
#         return None
    
#     def _parse_count(self, text: str) -> int:
#         """Parse counts like '25K' -> 25000"""
#         try:
#             text = text.strip().upper().replace(',', '')
#             multiplier = 1
            
#             if 'K' in text:
#                 multiplier = 1000
#                 text = text.replace('K', '')
#             elif 'M' in text:
#                 multiplier = 1000000
#                 text = text.replace('M', '')
            
#             import re
#             match = re.search(r'[\d.]+', text)
#             if match:
#                 return int(float(match.group()) * multiplier)
#         except:
#             pass
#         return 0

# import asyncio
# import time
# import pickle
# import os
# import re
# from typing import Dict, List, Optional
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException, NoSuchElementException
# from bs4 import BeautifulSoup
# import undetected_chromedriver as uc
# from app.config import settings
# import logging

# logger = logging.getLogger(__name__)

# class LinkedInScraper:
#     def __init__(self, email=None, password=None, skip_browser: bool = False):
#         self.driver = None
#         self.email = email or settings.LINKEDIN_EMAIL
#         self.password = password or settings.LINKEDIN_PASSWORD
#         self.cookies_file = "linkedin_cookies.pkl"
#         self.skip_browser = skip_browser
#         if self.skip_browser:
#             logger.info("🔧 LinkedInScraper started in skip_browser/test mode - no browser will be launched")
#             return
#         self.setup_driver()
        
#         # Try to load existing session
#         if os.path.exists(self.cookies_file):
#             logger.info("🔑 Found existing cookies, loading...")
#             self.load_cookies()
#             if self.verify_login():
#                 logger.info("✅ Using existing valid session")
#                 return
#             else:
#                 logger.warning("⚠️ Saved cookies expired, deleting...")
#                 os.remove(self.cookies_file)
        
#         # Need to login
#         if self.email and self.password:
#             self.login()
#         else:
#             logger.error("❌ No LinkedIn credentials provided")
#             raise Exception("LinkedIn credentials required")
    
#     def setup_driver(self):
#         """Initialize Chrome driver WITHOUT headless mode for manual verification"""
#         options = uc.ChromeOptions()
        
#         # Essential options only - NO HEADLESS MODE for manual verification
#         options.add_argument('--no-sandbox')
#         options.add_argument('--disable-dev-shm-usage')
#         options.add_argument('--disable-blink-features=AutomationControlled')
#         options.add_argument('--window-size=1920,1080')
#         options.add_argument('--start-maximized')
#         options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
#         try:
#             self.driver = uc.Chrome(options=options)
#         except Exception as e:
#             logger.warning(f"⚠️ Failed with options: {e}")
#             self.driver = uc.Chrome(use_subprocess=True)
        
#         # Remove webdriver detection
#         try:
#             self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
#         except:
#             pass
        
#         logger.info("✅ Selenium driver initialized (visible mode for manual verification)")

#     def _slugify(self, page_id: str) -> str:
#         """Normalize page_id into a slug safe for URLs and filenames."""
#         if not page_id:
#             return ""
#         slug = str(page_id).strip().lower()
#         # Replace spaces and slashes with dashes
#         slug = re.sub(r"[\s/]+", "-", slug)
#         # Remove characters except alphanum and dashes
#         slug = re.sub(r"[^a-z0-9\-]", "", slug)
#         # Collapse multiple dashes
#         slug = re.sub(r"\-{2,}", "-", slug)
#         return slug
    
#     def save_cookies(self):
#         """Save session cookies to file"""
#         try:
#             cookies = self.driver.get_cookies()
#             with open(self.cookies_file, 'wb') as f:
#                 pickle.dump(cookies, f)
#             logger.info("✅ Saved session cookies")
#         except Exception as e:
#             logger.error(f"❌ Failed to save cookies: {e}")
    
#     def load_cookies(self):
#         """Load saved session cookies"""
#         try:
#             self.driver.get("https://www.linkedin.com")
#             time.sleep(2)
            
#             with open(self.cookies_file, 'rb') as f:
#                 cookies = pickle.load(f)
            
#             for cookie in cookies:
#                 try:
#                     self.driver.add_cookie(cookie)
#                 except Exception as e:
#                     logger.debug(f"Skipped cookie: {e}")
            
#             self.driver.refresh()
#             time.sleep(3)
#             logger.info("✅ Loaded saved cookies")
#         except Exception as e:
#             logger.error(f"❌ Failed to load cookies: {e}")
    
#     def verify_login(self) -> bool:
#         """Check if currently logged in to LinkedIn"""
#         try:
#             self.driver.get("https://www.linkedin.com/feed")
#             time.sleep(3)
            
#             current_url = self.driver.current_url
#             if "feed" in current_url or "mynetwork" in current_url:
#                 logger.info("✅ Login verified - session is valid")
#                 return True
#             else:
#                 logger.warning(f"⚠️ Not logged in - current URL: {current_url}")
#                 return False
#         except Exception as e:
#             logger.error(f"❌ Login verification failed: {e}")
#             return False
    
#     def login(self):
#         """Login to LinkedIn with MANUAL CHALLENGE HANDLING"""
#         try:
#             logger.info("🔐 Logging into LinkedIn...")
#             self.driver.get("https://www.linkedin.com/login")
#             time.sleep(3)
            
#             # Check if already logged in
#             if "feed" in self.driver.current_url:
#                 logger.info("✅ Already logged in!")
#                 self.save_cookies()
#                 return
            
#             # Enter email
#             logger.info("📧 Entering email...")
#             email_field = self.driver.find_element(By.ID, "username")
#             email_field.clear()
#             email_field.send_keys(self.email)
#             time.sleep(1)
            
#             # Enter password
#             logger.info("🔑 Entering password...")
#             password_field = self.driver.find_element(By.ID, "password")
#             password_field.clear()
#             password_field.send_keys(self.password)
#             time.sleep(1)
            
#             # Click login button
#             logger.info("👆 Clicking login button...")
#             login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
#             login_button.click()
            
#             # Wait for response
#             time.sleep(8)
            
#             current_url = self.driver.current_url
#             logger.info(f"📍 Current URL after login attempt: {current_url}")
            
#             # ✅✅✅ HANDLE SECURITY CHECKPOINT/CHALLENGE ✅✅✅
#             if "checkpoint" in current_url or "challenge" in current_url:
#                 logger.warning("=" * 80)
#                 logger.warning("⚠️⚠️⚠️ LINKEDIN SECURITY CHECKPOINT DETECTED! ⚠️⚠️⚠️")
#                 logger.warning("=" * 80)
#                 logger.warning("🖱️  A BROWSER WINDOW IS OPEN - Please look at it!")
#                 logger.warning("📧 LinkedIn is asking for verification")
#                 logger.warning("✅ Complete the challenge in the browser:")
#                 logger.warning("   - Enter verification code from email/phone")
#                 logger.warning("   - Solve CAPTCHA if shown")
#                 logger.warning("   - Click 'Submit' or 'Verify'")
#                 logger.warning("⏳ Waiting up to 3 MINUTES for you to complete verification...")
#                 logger.warning("=" * 80)
                
#                 # Wait for user to complete challenge (3 minutes timeout)
#                 for i in range(180):
#                     time.sleep(1)
#                     current_url = self.driver.current_url
                    
#                     # Check if user completed challenge successfully
#                     if "feed" in current_url or "mynetwork" in current_url:
#                         logger.info("=" * 80)
#                         logger.info("✅✅✅ CHALLENGE COMPLETED SUCCESSFULLY! ✅✅✅")
#                         logger.info("=" * 80)
#                         logger.info("💾 Saving your session for future use...")
#                         self.save_cookies()
#                         logger.info("✅ Session saved! Future requests won't need verification.")
#                         return True
                    
#                     # Log progress every 15 seconds
#                     if i > 0 and i % 15 == 0:
#                         remaining = 180 - i
#                         logger.warning(f"⏳ Still waiting... {remaining} seconds remaining")
#                         logger.warning(f"   Current page: {current_url[:50]}...")
                
#                 # Timeout reached
#                 logger.error("=" * 80)
#                 logger.error("❌ TIMEOUT - Challenge not completed in 3 minutes")
#                 logger.error("=" * 80)
#                 raise Exception("LinkedIn security challenge timeout - verification not completed")
            
#             # Normal login without challenge
#             if "feed" in current_url or "mynetwork" in current_url:
#                 logger.info("✅ Successfully logged in (no challenge)")
#                 self.save_cookies()
#                 return True
#             elif "authwall" in current_url or "login" in current_url:
#                 logger.error("❌ Login failed - still on login page")
#                 raise Exception("LinkedIn login failed - check credentials")
#             else:
#                 logger.warning(f"⚠️ Unexpected URL after login: {current_url}")
#                 # Still save cookies just in case
#                 self.save_cookies()
#                 return True
        
#         except Exception as e:
#             logger.error(f"❌ Login process failed: {str(e)}")
#             raise
    
#     def close(self):
#         """Close the browser driver"""
#         if self.driver:
#             self.driver.quit()
#             logger.info("❌ Browser closed")
    
#     async def scrape_page(self, page_id: str) -> Dict:
#         """Main scraping method with auth wall detection"""
#         try:
#             page_slug = self._slugify(page_id)
#             logger.info(f"🔍 Starting scrape for page: {page_id} (slug: {page_slug})")
            
#             url = f"https://www.linkedin.com/company/{page_slug}/"
#             self.driver.get(url)
#             await asyncio.sleep(5)
            
#             # Check for auth wall
#             page_source = self.driver.page_source
#             current_url = self.driver.current_url
            
#             if "authwall" in current_url or "auth_wall" in page_source:
#                 logger.error("🚫 Hit LinkedIn auth wall - session expired!")
#                 logger.info("🔄 Attempting to re-login...")
                
#                 # Delete old cookies
#                 if os.path.exists(self.cookies_file):
#                     os.remove(self.cookies_file)
                
#                 # Re-login (will trigger manual verification if needed)
#                 self.login()
                
#                 # Try accessing page again
#                 self.driver.get(url)
#                 await asyncio.sleep(5)
                
#                 # Refresh page_source and current_url after re-login
#                 page_source = self.driver.page_source
#                 current_url = self.driver.current_url
                
#                 # Check again
#                 if "authwall" in current_url:
#                     raise Exception("Failed to bypass auth wall after re-login")
            
#             # Check if page exists
#             if "Page not found" in page_source or "404" in self.driver.title:
#                 raise ValueError(f"LinkedIn page '{page_id}' not found")
            
#             # Scrape data
#             basic_info = await self._scrape_basic_info(page_slug)
#             posts = await self._scrape_posts(page_slug, limit=20)
#             employees = await self._scrape_employees(page_slug, limit=50)
            
#             result = {
#                 **basic_info,
#                 "posts": posts,
#                 "employees": employees
#             }
            
#             logger.info(f"✅ Successfully scraped page: {page_id} (slug: {page_slug})")
#             return result
            
#         except Exception as e:
#             logger.error(f"❌ Scraping failed for {page_id} (slug: {page_slug}): {str(e)}")
#             raise
    
#     async def _scrape_basic_info(self, page_id: str) -> Dict:
#         """Extract basic page information"""
#         soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        
#         data = {
#             "page_id": page_id,
#             "url": self.driver.current_url
#         }
        
#         try:
#             # Page Name
#             name_elem = soup.select_one('h1.org-top-card-summary__title')
#             if not name_elem:
#                 name_elem = soup.select_one('h1.org-top-card-summary-info-list__title')
#             data['name'] = name_elem.text.strip() if name_elem else page_id
            
#             # LinkedIn ID
#             data['linkedin_id'] = self._extract_linkedin_id()
            
#             # Profile Picture
#             img_elem = soup.select_one('img.org-top-card-primary-content__logo')
#             if not img_elem:
#                 img_elem = soup.select_one('img[alt*="logo"]')
#             data['profile_picture'] = img_elem.get('src') if img_elem else None
            
#             # Description
#             desc_elem = soup.select_one('p.org-top-card-summary__tagline')
#             if not desc_elem:
#                 desc_elem = soup.select_one('p.break-words')
#             data['description'] = desc_elem.text.strip() if desc_elem else None
            
#             # Website
#             website_elem = soup.select_one('a.link-without-visited-state[href*="http"]')
#             if not website_elem:
#                 website_elem = soup.select_one('a[data-tracking-control-name*="website"]')
#             data['website'] = website_elem.get('href') if website_elem else None
            
#             # Industry
#             industry_text = None
#             info_items = soup.select('div.org-top-card-summary-info-list__info-item')
#             for item in info_items:
#                 if 'Industry' in item.text or 'industry' in item.text.lower():
#                     industry_text = item.text.replace('Industry', '').strip()
#                     break
#             data['industry'] = industry_text
            
#             # Followers
#             followers_text = None
#             for item in info_items:
#                 if 'follower' in item.text.lower():
#                     followers_text = item.text
#                     break
#             data['followers_count'] = self._parse_count(followers_text if followers_text else "0")
            
#             # Head Count
#             headcount_text = None
#             for item in info_items:
#                 if 'employee' in item.text.lower():
#                     headcount_text = item.text.strip()
#                     break
#             data['head_count'] = headcount_text
            
#             # Specialities
#             specialities = []
#             spec_section = soup.select('dd.org-page-details__definition-text')
#             for spec in spec_section:
#                 items = spec.text.strip().split(',')
#                 specialities.extend([s.strip() for s in items])
#             data['specialities'] = specialities[:10]
#             page_slug = self._slugify(page_id)
#             logger.info(f"✅ Basic info scraped for {page_slug}")
#             return data
            
#         except Exception as e:
#             logger.error(f"❌ Error scraping basic info: {str(e)}")
#             return data
    
#     async def _scrape_posts(self, page_id: str, limit: int = 20) -> List[Dict]:
#         """Scrape recent posts"""
#         posts = []
        
#         try:
#             page_slug = self._slugify(page_id)
#             posts_url = f"https://www.linkedin.com/company/{page_slug}/posts/"
#             logger.info(f"📝 Navigating to posts: {posts_url}")
#             self.driver.get(posts_url)
            
#             await asyncio.sleep(10)
            
#             # Wait for posts container or a generic 'article' tag
#             try:
#                 wait = WebDriverWait(self.driver, 20)
#                 wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.scaffold-finite-scroll__content")))
#                 logger.info("✅ Posts container found")
#             except TimeoutException:
#                 try:
#                     wait.until(EC.presence_of_element_located((By.TAG_NAME, "article")))
#                     logger.info("✅ 'article' tag found (fallback for posts)")
#                 except TimeoutException:
#                     logger.warning("⚠️ Posts container not found (tried scaffold and article)")
            
#             # Scroll to load posts
#             for i in range(10):
#                 self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#                 await asyncio.sleep(3)
#                 logger.info(f"📜 Scroll {i+1}/10")
            
#             # Save debug
#             debug_path = f"debug_{page_slug}_posts.html"
#             with open(debug_path, "w", encoding="utf-8") as f:
#                 f.write(self.driver.page_source)
#             logger.info(f"💾 Saved debug HTML to {debug_path}")
            
#             soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
#             # Try multiple selectors
#             post_elements = soup.select('div.feed-shared-update-v2')
#             if not post_elements:
#                 post_elements = soup.select('div[data-urn*="activity"]')
#             if not post_elements:
#                 post_elements = soup.select('article')
#             if not post_elements:
#                 post_elements = soup.select('article.feed-shared-update-v2')
            
#             logger.info(f"📝 Found {len(post_elements)} post elements")
            
#             for idx, post_elem in enumerate(post_elements[:limit]):
#                 try:
#                     post_data = {
#                         "post_id": f"{page_slug}_post_{idx}_{int(time.time())}",
#                         "page_id": page_slug,
#                         "content": "",
#                         "likes_count": 0,
#                         "comments_count": 0,
#                         "shares_count": 0,
#                         "media_urls": [],
#                         "comments": []
#                     }
                    
#                     # Extract post content
#                     content_elem = post_elem.select_one('div.feed-shared-text')
#                     if not content_elem:
#                         content_elem = post_elem.select_one('span.break-words')
#                     if content_elem:
#                         post_data['content'] = content_elem.text.strip()
                    
#                     # Likes
#                     likes_elem = post_elem.select_one('span.social-details-social-counts__reactions-count')
#                     if likes_elem:
#                         post_data['likes_count'] = self._parse_count(likes_elem.text)
                    
#                     # Comments
#                     comments_elem = post_elem.select_one('button[aria-label*="comment"]')
#                     if comments_elem:
#                         post_data['comments_count'] = self._parse_count(comments_elem.text)
                    
#                     # Media
#                     media_elems = post_elem.select('img.feed-shared-image__image')
#                     post_data['media_urls'] = [img.get('src') for img in media_elems if img.get('src')]
                    
#                     posts.append(post_data)
#                     logger.info(f"✅ Parsed post {idx+1}")
                    
#                 except Exception as e:
#                     logger.warning(f"⚠️ Failed to parse post {idx}: {e}")
#                     continue
            
#             logger.info(f"✅ Scraped {len(posts)} posts for {page_slug}")
#             return posts
            
#         except Exception as e:
#             logger.error(f"❌ Error scraping posts: {e}")
#             return posts
    
#     async def _scrape_employees(self, page_id: str, limit: int = 50) -> List[Dict]:
#         """Scrape employees"""
#         employees = []
        
#         try:
#             page_slug = self._slugify(page_id)
#             people_url = f"https://www.linkedin.com/company/{page_slug}/people/"
#             logger.info(f"👥 Navigating to people: {people_url}")
#             self.driver.get(people_url)
            
#             await asyncio.sleep(10)
            
#             # Wait for people grid or fallback selectors
#             try:
#                 wait = WebDriverWait(self.driver, 20)
#                 wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "ul.scaffold-finite-scroll__content")))
#                 logger.info("✅ People grid found")
#             except TimeoutException:
#                 try:
#                     wait.until(EC.presence_of_element_located((By.TAG_NAME, "li")))
#                     logger.info("✅ 'li' tag found (fallback for people list)")
#                 except TimeoutException:
#                     logger.warning("⚠️ People grid not found")
            
#             # Scroll
#             for i in range(8):
#                 self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#                 await asyncio.sleep(3)
#                 logger.info(f"📜 Scroll {i+1}/8")
            
#             # Save debug
#             debug_path = f"debug_{page_slug}_people.html"
#             with open(debug_path, "w", encoding="utf-8") as f:
#                 f.write(self.driver.page_source)
#             logger.info(f"💾 Saved debug HTML to {debug_path}")
            
#             soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
#             # Try multiple selectors
#             people_elements = soup.select('li.org-people-profile-card__profile-card-spacing')
#             if not people_elements:
#                 people_elements = soup.select('div.org-people-profile-card')
#             if not people_elements:
#                 people_elements = soup.select('li.artdeco-list__item')
            
#             logger.info(f"👥 Found {len(people_elements)} people elements")
            
#             for idx, person_elem in enumerate(people_elements[:limit]):
#                 try:
#                     employee_data = {
#                         "user_id": f"{page_slug}_user_{idx}_{int(time.time())}",
#                         "name": "",
#                         "profile_url": "",
#                         "profile_picture": None,
#                         "headline": None,
#                         "current_company": page_slug
#                     }
                    
#                     # Name
#                     name_elem = person_elem.select_one('span.org-people-profile-card__profile-title')
#                     if not name_elem:
#                         name_elem = person_elem.select_one('div.artdeco-entity-lockup__title')
#                     if name_elem:
#                         employee_data['name'] = name_elem.text.strip()
                    
#                     # Profile URL
#                     link_elem = person_elem.select_one('a[href*="/in/"]')
#                     if link_elem:
#                         employee_data['profile_url'] = link_elem.get('href', '')
                    
#                     # Picture
#                     img_elem = person_elem.select_one('img')
#                     if img_elem:
#                         employee_data['profile_picture'] = img_elem.get('src')
                    
#                     # Headline
#                     headline_elem = person_elem.select_one('div.artdeco-entity-lockup__subtitle')
#                     if headline_elem:
#                         employee_data['headline'] = headline_elem.text.strip()
                    
#                     if employee_data['name']:
#                         employees.append(employee_data)
#                         logger.info(f"✅ Parsed employee {idx+1}")
                    
#                 except Exception as e:
#                     logger.warning(f"⚠️ Failed to parse employee {idx}: {e}")
#                     continue
            
#             logger.info(f"✅ Scraped {len(employees)} employees for {page_slug}")
#             return employees
            
#         except Exception as e:
#             logger.error(f"❌ Error scraping employees: {e}")
#             return employees
    
#     def _extract_linkedin_id(self) -> Optional[str]:
#         """Extract LinkedIn organization ID"""
#         try:
#             page_source = self.driver.page_source
#             if 'organizationId' in page_source:
#                 import re
#                 match = re.search(r'"organizationId":"(\d+)"', page_source)
#                 if match:
#                     return match.group(1)
#         except:
#             pass
#         return None
    
#     def _parse_count(self, text: str) -> int:
#         """Parse counts like '25K' -> 25000"""
#         try:
#             text = text.strip().upper().replace(',', '')
#             multiplier = 1
            
#             if 'K' in text:
#                 multiplier = 1000
#                 text = text.replace('K', '')
#             elif 'M' in text:
#                 multiplier = 1000000
#                 text = text.replace('M', '')
            
#             import re
#             match = re.search(r'[\d.]+', text)
#             if match:
#                 return int(float(match.group()) * multiplier)
#         except:
#             pass
#         return 0

import asyncio
import time
import pickle
import os
import re
from typing import Dict, List, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

class LinkedInScraper:
    def __init__(self, email=None, password=None, skip_browser: bool = False, headless: bool = False):
        self.driver = None
        self.email = email or os.getenv('LINKEDIN_EMAIL')
        self.password = password or os.getenv('LINKEDIN_PASSWORD')
        self.cookies_file = "/app/data/uploads/linkedin_cookies.pkl"
        self.skip_browser = skip_browser
        self.headless = headless or os.getenv("HEADLESS_MODE", "false").lower() == "true"

        
        if self.skip_browser:
            logger.info("🔧 LinkedInScraper started in skip_browser/test mode - no browser will be launched")
            return
            
        self.setup_driver()
        
        # Try to load existing session
        if os.path.exists(self.cookies_file):
            logger.info("🔑 Found existing cookies, loading...")
            self.load_cookies()
            if self.verify_login():
                logger.info("✅ Using existing valid session")
                return
            else:
                logger.warning("⚠️ Saved cookies expired, deleting...")
                os.remove(self.cookies_file)
        
        # Need to login
        if self.email and self.password:
            self.login()
        else:
            logger.error("❌ No LinkedIn credentials provided")
            raise Exception("LinkedIn credentials required")
    
    def setup_driver(self):
        """Initialize Chrome driver (Docker + LinkedIn safe configuration)"""

        options = webdriver.ChromeOptions()

        # ===== REQUIRED FOR DOCKER =====
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-setuid-sandbox")

        # ===== HEADLESS MODE (recommended in Docker) =====
        if self.headless:
            options.add_argument("--headless=new")
            logger.info("🔧 Running in HEADLESS mode")

        # ===== ANTI-DETECTION SETTINGS =====
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

        # ===== BROWSER BEHAVIOR =====
        options.add_argument("--start-maximized")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-infobars")
        options.add_argument("--log-level=3")

        # ===== USER AGENT (IMPORTANT FOR LINKEDIN) =====
        options.add_argument(
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )

        try:
            self.driver = webdriver.Chrome(options=options)

            # Hide webdriver flag
            self.driver.execute_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            )

            logger.info("✅ Chrome WebDriver initialized successfully")

        except Exception as e:
            logger.error(f"❌ Failed to initialize Chrome WebDriver: {e}")
            raise


    def _slugify(self, page_id: str) -> str:
        """Normalize page_id into a slug safe for URLs"""
        if not page_id:
            return ""
        
        # Handle if it's already a LinkedIn URL
        if 'linkedin.com/company/' in page_id:
            match = re.search(r'linkedin\.com/company/([^/?]+)', page_id)
            if match:
                return match.group(1).strip('/')
        
        slug = str(page_id).strip().lower()
        
        # Remove common company suffixes
        slug = re.sub(r'\s+(inc|llc|ltd|corp|corporation|limited|pvt|private)\.?\s*$', '', slug, flags=re.IGNORECASE)
        
        # Replace spaces/separators with dashes
        slug = re.sub(r'[\s_/\\]+', '-', slug)
        
        # Remove special characters
        slug = re.sub(r'[^a-z0-9\-]', '', slug)
        
        # Collapse multiple dashes
        slug = re.sub(r'-+', '-', slug)
        slug = slug.strip('-')
        
        logger.info(f"🔧 Slugified '{page_id}' -> '{slug}'")
        return slug
    
    def save_cookies(self):
        """Save session cookies to file"""
        try:
            cookies = self.driver.get_cookies()
            with open(self.cookies_file, 'wb') as f:
                pickle.dump(cookies, f)
            logger.info("✅ Saved session cookies")
        except Exception as e:
            logger.error(f"❌ Failed to save cookies: {e}")
    
    def load_cookies(self):
        """Load saved session cookies"""
        try:
            self.driver.get("https://www.linkedin.com")
            time.sleep(2)
            
            with open(self.cookies_file, 'rb') as f:
                cookies = pickle.load(f)
            
            for cookie in cookies:
                try:
                    self.driver.add_cookie(cookie)
                except Exception as e:
                    logger.debug(f"Skipped cookie: {e}")
            
            self.driver.refresh()
            time.sleep(3)
            logger.info("✅ Loaded saved cookies")
        except Exception as e:
            logger.error(f"❌ Failed to load cookies: {e}")
    
    def verify_login(self) -> bool:
        """Check if currently logged in to LinkedIn"""
        try:
            self.driver.get("https://www.linkedin.com/feed")
            time.sleep(3)
            
            current_url = self.driver.current_url
            if "feed" in current_url or "mynetwork" in current_url:
                logger.info("✅ Login verified - session is valid")
                return True
            else:
                logger.warning(f"⚠️ Not logged in - current URL: {current_url}")
                return False
        except Exception as e:
            logger.error(f"❌ Login verification failed: {e}")
            return False
    
    def login(self):
        """Login to LinkedIn with Robust Wait and Selector Handling"""
        try:
            logger.info("🔐 Logging into LinkedIn...")
            self.driver.get("https://www.linkedin.com/login")
            
            # Wait for potential redirects
            time.sleep(5)
            
            # 1. Check if we were redirected to Feed immediately
            if "feed" in self.driver.current_url or "mynetwork" in self.driver.current_url:
                logger.info("✅ Already logged in!")
                self.save_cookies()
                return

            # 2. handle different Login Page Variations
            logger.info("📧 Finding email field...")
            email_field = None
            
            try:
                # Wait up to 10 seconds for the username field
                wait = WebDriverWait(self.driver, 10)
                
                # Try selector 1: Standard 'username'
                try:
                    email_field = wait.until(EC.presence_of_element_located((By.ID, "username")))
                except:
                    # Try selector 2: Older 'session_key'
                    logger.info("⚠️ 'username' ID not found, trying 'session_key'...")
                    email_field = wait.until(EC.presence_of_element_located((By.ID, "session_key")))
            
            except TimeoutException:
                # If neither is found, we might be on a "Join Now" page or Security Check
                logger.error(f"❌ Could not find login fields. Current URL: {self.driver.current_url}")
                logger.error(f"Page Title: {self.driver.title}")
                
                # Snap a debug screenshot/html if possible (optional)
                with open("/app/data/uploads/login_fail_debug.html", "w") as f:
                    f.write(self.driver.page_source)
                
                raise Exception("Login page structure changed or intercepted by security check")

            # 3. Enter Credentials
            logger.info("📧 Entering email...")
            email_field.clear()
            email_field.send_keys(self.email)
            time.sleep(1)
            
            logger.info("🔑 Entering password...")
            try:
                password_field = self.driver.find_element(By.ID, "password")
            except NoSuchElementException:
                password_field = self.driver.find_element(By.ID, "session_password")
                
            password_field.clear()
            password_field.send_keys(self.password)
            time.sleep(1)
            
            # 4. Click Login
            logger.info("👆 Clicking login button...")
            try:
                login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            except NoSuchElementException:
                login_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Sign in')]")
                
            login_button.click()
            
            # 5. Handle Post-Login (Security Checks)
            time.sleep(8)
            current_url = self.driver.current_url
            logger.info(f"📍 Current URL after login attempt: {current_url}")
            
            if "checkpoint" in current_url or "challenge" in current_url:
                logger.warning("⚠️⚠️⚠️ LINKEDIN SECURITY CHECKPOINT DETECTED! ⚠️⚠️⚠️")
                # ... (rest of your existing challenge handling logic here) ...
                if self.headless:
                    raise Exception("LinkedIn security challenge requires manual verification.")

            if "feed" in current_url or "mynetwork" in current_url:
                logger.info("✅ Successfully logged in")
                self.save_cookies()
                return True
            elif "authwall" in current_url:
                logger.error("❌ Still stuck on Authwall after login attempt")
                raise Exception("Authwall persistence")
            else:
                # One last check - sometimes the URL doesn't change but we are logged in
                if len(self.driver.get_cookies()) > 5:
                        logger.info("✅ Cookies look valid, assuming login success")
                        self.save_cookies()
                        return True
                
                logger.warning(f"⚠️ Unexpected URL after login: {current_url}")
                return True
        
        except Exception as e:
            logger.error(f"❌ Login process failed: {str(e)}")
            raise
    
    def close(self):
        """Close the browser driver"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("❌ Browser closed")
            except Exception as e:
                logger.warning(f"⚠️ Error closing browser: {e}")
    
    async def scrape_page(self, page_id: str) -> Dict:
        """Main scraping method with auth wall detection"""
        try:
            page_slug = self._slugify(page_id)
            logger.info(f"🔍 Starting scrape for page: '{page_id}' (slug: '{page_slug}')")
            
            url = f"https://www.linkedin.com/company/{page_slug}/"
            logger.info(f"🌐 Navigating to: {url}")
            self.driver.get(url)
            
            # Wait for page load
            time.sleep(8)
            
            page_source = self.driver.page_source
            current_url = self.driver.current_url
            
            # Check for auth wall
            if "authwall" in current_url or "auth_wall" in page_source.lower():
                logger.error("🚫 Hit LinkedIn auth wall - session expired!")
                logger.info("🔄 Attempting to re-login...")
                
                if os.path.exists(self.cookies_file):
                    os.remove(self.cookies_file)
                
                self.login()
                
                self.driver.get(url)
                time.sleep(8)
                
                page_source = self.driver.page_source
                current_url = self.driver.current_url
                
                if "authwall" in current_url:
                    raise Exception("Failed to bypass auth wall after re-login")
            
            # Check if page exists
            if "Page not found" in page_source or "404" in self.driver.title or "/404" in current_url:
                raise ValueError(f"LinkedIn page '{page_id}' not found. Tried URL: {url}")
            
            # Scrape data
            basic_info = await self._scrape_basic_info(page_slug)
            posts = await self._scrape_posts(page_slug, limit=20)
            employees = await self._scrape_employees(page_slug, limit=50)
            
            result = {
                **basic_info,
                "posts": posts,
                "employees": employees
            }
            
            logger.info(f"✅ Successfully scraped page: {page_id} - {len(posts)} posts, {len(employees)} employees")
            return result
            
        except Exception as e:
            logger.error(f"❌ Scraping failed for {page_id}: {str(e)}")
            raise
    
    async def _scrape_basic_info(self, page_id: str) -> Dict:
        """Extract basic page information - FIXED VERSION"""
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        
        data = {
            "page_id": page_id,
            "url": self.driver.current_url
        }
        
        try:
            # Page Name - multiple selectors
            name_elem = (soup.select_one('h1.org-top-card-summary__title') or 
                        soup.select_one('h1.org-top-card-summary-info-list__title') or
                        soup.select_one('h1[dir="ltr"]'))
            data['name'] = name_elem.text.strip() if name_elem else page_id
            
            # LinkedIn ID
            data['linkedin_id'] = self._extract_linkedin_id()
            
            # Profile Picture
            img_elem = (soup.select_one('img.org-top-card-primary-content__logo') or
                       soup.select_one('img[alt*="logo"]') or
                       soup.select_one('div.org-top-card-primary-content__logo-container img'))
            data['profile_picture'] = img_elem.get('src') if img_elem else None
            
            # Description - FIXED with more selectors
            desc_elem = (soup.select_one('p.org-top-card-summary__tagline') or
                        soup.select_one('p.break-words.white-space-pre-wrap.t-black--light') or
                        soup.select_one('div.org-top-card-summary__tagline p') or
                        soup.select_one('p[class*="tagline"]'))
            
            if desc_elem:
                data['description'] = desc_elem.text.strip()
            else:
                # Try to get from About section
                about_section = soup.select_one('section[data-section="about"]')
                if about_section:
                    about_text = about_section.select_one('p')
                    if about_text:
                        data['description'] = about_text.text.strip()
            
            # Website - FIXED to exclude LinkedIn premium links
            website_links = soup.select('a[href*="http"]')
            for link in website_links:
                href = link.get('href', '')
                # Skip LinkedIn internal links
                if 'linkedin.com' not in href and 'li.com' not in href:
                    data['website'] = href
                    break
            
            # If no external website found, try specific selectors
            if not data.get('website'):
                website_elem = soup.select_one('a.link-without-visited-state:not([href*="linkedin.com"])')
                if website_elem:
                    data['website'] = website_elem.get('href')
            
            # Industry, Followers, Headcount - FIXED parsing
            info_items = soup.select('div.org-top-card-summary-info-list__info-item')
            
            data['followers_count'] = 0
            data['head_count'] = None
            data['industry'] = None
            
            for item in info_items:
                text = item.text.strip()
                text_lower = text.lower()
                
                # Industry
                if 'industry' in text_lower or 'industries' in text_lower:
                    # Remove the label and get just the value
                    lines = text.split('\n')
                    if len(lines) > 1:
                        data['industry'] = lines[-1].strip()
                    else:
                        data['industry'] = text.replace('Industry', '').replace('Industries', '').strip()
                
                # Followers - FIXED to parse correctly
                elif 'follower' in text_lower:
                    # Extract just the number
                    follower_text = re.search(r'([\d,KMB.]+)\s*follower', text, re.IGNORECASE)
                    if follower_text:
                        data['followers_count'] = self._parse_count(follower_text.group(1))
                
                # Employees/Head count
                elif 'employee' in text_lower or 'associated member' in text_lower:
                    data['head_count'] = text.strip()
            
            # Specialities
            specialities = []
            spec_section = soup.select('dd.org-page-details__definition-text')
            for spec in spec_section:
                items = spec.text.strip().split(',')
                specialities.extend([s.strip() for s in items if s.strip()])
            data['specialities'] = specialities[:10]
            
            logger.info(f"✅ Basic info scraped for {page_id}: {data.get('name', 'Unknown')}")
            logger.info(f"   Description: {data.get('description')[:50] if data.get('description') else 'None'}...")
            logger.info(f"   Industry: {data.get('industry', 'None')}")
            logger.info(f"   Website: {data.get('website', 'None')}")
            logger.info(f"   Followers: {data.get('followers_count', 0)}")
            
            return data
            
        except Exception as e:
            logger.error(f"❌ Error scraping basic info: {str(e)}")
            return data
    
    async def _scrape_posts(self, page_id: str, limit: int = 20) -> List[Dict]:
        """Scrape recent posts - IMPROVED with better scrolling"""
        posts = []
        
        try:
            page_slug = self._slugify(page_id)
            posts_url = f"https://www.linkedin.com/company/{page_slug}/posts/"
            logger.info(f"📝 Navigating to posts: {posts_url}")
            self.driver.get(posts_url)
            
            time.sleep(5)
            
            # Strategic scrolling - like job scraper
            logger.info("📜 Scrolling to load posts...")
            for i in range(15):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                
                # Scroll back up slightly every 3 iterations
                if i % 3 == 0:
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight - 500);")
                    time.sleep(1)
                
                if i % 5 == 0:
                    logger.info(f"📜 Scroll iteration {i+1}/15")
            
            time.sleep(3)
            
            # Save debug HTML
            debug_path = f"debug_{page_slug}_posts.html"
            with open(debug_path, "w", encoding="utf-8") as f:
                f.write(self.driver.page_source)
            logger.info(f"💾 Saved debug HTML to {debug_path}")
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Try multiple selectors
            post_elements = []
            selectors = [
                'div.feed-shared-update-v2',
                'div[data-urn*="activity"]',
                'li.profile-creator-shared-feed-update__container',
                'div.occludable-update',
                'article'
            ]
            
            for selector in selectors:
                post_elements = soup.select(selector)
                if post_elements:
                    logger.info(f"✅ Found {len(post_elements)} posts using selector: {selector}")
                    break
            
            if not post_elements:
                logger.warning(f"⚠️ No posts found for {page_slug}. Check debug HTML file.")
                return posts
            
            for idx, post_elem in enumerate(post_elements[:limit]):
                try:
                    post_data = {
                        "post_id": f"{page_slug}_post_{idx}_{int(time.time())}",
                        "page_id": page_slug,
                        "content": "",
                        "likes_count": 0,
                        "comments_count": 0,
                        "shares_count": 0,
                        "media_urls": [],
                        "comments": []
                    }
                    
                    # Extract content
                    content_elem = (post_elem.select_one('div.feed-shared-text') or
                                   post_elem.select_one('span.break-words') or
                                   post_elem.select_one('div.feed-shared-update-v2__description-wrapper'))
                    
                    if content_elem:
                        post_data['content'] = content_elem.get_text(strip=True, separator=' ')
                    
                    # Likes - FIXED to get actual likes
                    likes_elem = post_elem.select_one('span.social-details-social-counts__reactions-count')
                    if likes_elem:
                        post_data['likes_count'] = self._parse_count(likes_elem.get_text(strip=True))
                    
                    # Comments - FIXED to parse correctly
                    comments_elem = post_elem.select_one('button[aria-label*="comment"]')
                    if comments_elem:
                        # Get text from button
                        comment_text = comments_elem.get_text(strip=True)
                        # Parse the number
                        comment_match = re.search(r'(\d+)', comment_text)
                        if comment_match:
                            post_data['comments_count'] = int(comment_match.group(1))
                    
                    # Alternative comment selector
                    if post_data['comments_count'] == 0:
                        comment_count_elem = post_elem.select_one('span.social-details-social-counts__comments')
                        if comment_count_elem:
                            post_data['comments_count'] = self._parse_count(comment_count_elem.get_text(strip=True))
                    
                    # Media
                    media_elems = post_elem.select('img.feed-shared-image__image')
                    post_data['media_urls'] = [img.get('src') for img in media_elems if img.get('src')]
                    
                    if post_data['content'] or post_data['media_urls']:
                        posts.append(post_data)
                        logger.info(f"✅ Parsed post {len(posts)}: {post_data['content'][:50]}...")
                    
                except Exception as e:
                    logger.warning(f"⚠️ Failed to parse post {idx}: {e}")
                    continue
            
            logger.info(f"✅ Successfully scraped {len(posts)} posts for {page_slug}")
            return posts
            
        except Exception as e:
            logger.error(f"❌ Error scraping posts: {e}")
            return posts
    
    async def _scrape_employees(self, page_id: str, limit: int = 50) -> List[Dict]:
        """Scrape employees - IMPROVED with better scrolling"""
        employees = []
        
        try:
            page_slug = self._slugify(page_id)
            people_url = f"https://www.linkedin.com/company/{page_slug}/people/"
            logger.info(f"👥 Navigating to people: {people_url}")
            self.driver.get(people_url)
            
            time.sleep(5)
            
            # Strategic scrolling
            logger.info("📜 Scrolling to load employees...")
            for i in range(12):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                
                if i % 3 == 0:
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight - 500);")
                    time.sleep(1)
                
                if i % 4 == 0:
                    logger.info(f"📜 Scroll iteration {i+1}/12")
            
            time.sleep(3)
            
            # Save debug
            debug_path = f"debug_{page_slug}_people.html"
            with open(debug_path, "w", encoding="utf-8") as f:
                f.write(self.driver.page_source)
            logger.info(f"💾 Saved debug HTML to {debug_path}")
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Try multiple selectors
            people_elements = []
            selectors = [
                'li.org-people-profile-card__profile-card-spacing',
                'div.org-people-profile-card',
                'li.artdeco-list__item',
                'div.scaffold-finite-scroll__content li'
            ]
            
            for selector in selectors:
                people_elements = soup.select(selector)
                if people_elements:
                    logger.info(f"✅ Found {len(people_elements)} people using selector: {selector}")
                    break
            
            if not people_elements:
                logger.warning(f"⚠️ No employees found for {page_slug}. Check debug HTML file.")
                return employees
            
            for idx, person_elem in enumerate(people_elements[:limit]):
                try:
                    employee_data = {
                        "user_id": f"{page_slug}_user_{idx}_{int(time.time())}",
                        "name": "",
                        "profile_url": "",
                        "profile_picture": None,
                        "headline": None,
                        "current_company": page_slug
                    }
                    
                    # Name
                    name_elem = (person_elem.select_one('span.org-people-profile-card__profile-title') or
                                person_elem.select_one('div.artdeco-entity-lockup__title'))
                    
                    if name_elem:
                        employee_data['name'] = name_elem.get_text(strip=True)
                    
                    # Profile URL
                    link_elem = person_elem.select_one('a[href*="/in/"]')
                    if link_elem:
                        href = link_elem.get('href', '')
                        if '?' in href:
                            href = href.split('?')[0]
                        employee_data['profile_url'] = href
                    
                    # Picture
                    img_elem = person_elem.select_one('img')
                    if img_elem:
                        src = img_elem.get('src')
                        if src and 'media' in src:
                            employee_data['profile_picture'] = src
                    
                    # Headline
                    headline_elem = person_elem.select_one('div.artdeco-entity-lockup__subtitle')
                    if headline_elem:
                        employee_data['headline'] = headline_elem.get_text(strip=True)
                    
                    if employee_data['name']:
                        employees.append(employee_data)
                        logger.info(f"✅ Parsed employee {len(employees)}: {employee_data['name']}")
                    
                except Exception as e:
                    logger.warning(f"⚠️ Failed to parse employee {idx}: {e}")
                    continue
            
            logger.info(f"✅ Successfully scraped {len(employees)} employees for {page_slug}")
            return employees
            
        except Exception as e:
            logger.error(f"❌ Error scraping employees: {e}")
            return employees
    
    def _extract_linkedin_id(self) -> Optional[str]:
        """Extract LinkedIn organization ID"""
        try:
            page_source = self.driver.page_source
            if 'organizationId' in page_source:
                match = re.search(r'"organizationId":"(\d+)"', page_source)
                if match:
                    return match.group(1)
        except:
            pass
        return None
    
    def _parse_count(self, text: str) -> int:
        """Parse counts like '25K' -> 25000"""
        try:
            if not text:
                return 0
                
            text = text.strip().upper().replace(',', '').replace(' ', '')
            
            # Remove common words
            text = text.replace('FOLLOWERS', '').replace('COMMENTS', '').replace('LIKES', '')
            text = text.strip()
            
            multiplier = 1
            
            if 'K' in text:
                multiplier = 1000
                text = text.replace('K', '')
            elif 'M' in text:
                multiplier = 1000000
                text = text.replace('M', '')
            elif 'B' in text:
                multiplier = 1000000000
                text = text.replace('B', '')
            
            match = re.search(r'[\d.]+', text)
            if match:
                return int(float(match.group()) * multiplier)
        except Exception as e:
            logger.debug(f"Failed to parse count '{text}': {e}")
        return 0
    
    
    
    
    
    
    
    
    
