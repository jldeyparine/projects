"""
TruckerBoerse.net Job Scraper
Extracts job listings from all pages and detailed information from each job posting
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
from datetime import datetime

class TruckerBoerseJobScraper:
    def __init__(self, headless=True):
        """Initialize the scraper with Chrome WebDriver"""
        self.base_url = "https://www.truckerboerse.net/index.php?page=5140&js=&kat=lkw&stellenangebote_kraftfahrer="
        self.job_links = []
        self.job_data = []
        
        # Setup Chrome options
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 10)
        
    def extract_job_links_from_page(self):
        """Extract all job links from current page"""
        try:
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Find all job listing links
            job_links = soup.find_all('a', href=re.compile(r'kraftfahrer-jobs/\d+/'))
            
            for link in job_links:
                href = link.get('href')
                if href and href.startswith('https://www.truckerboerse.net/kraftfahrer-jobs/'):
                    if href not in self.job_links:
                        self.job_links.append(href)
                        print(f"  Found job link: {href}")
            
            return len(job_links)
        except Exception as e:
            print(f"Error extracting links: {e}")
            return 0
    
    def get_next_page_url(self, current_page):
        """Generate URL for next page"""
        return f"{self.base_url}{current_page}"
    
    def scrape_all_pages(self, max_pages=258):
        """Scrape job links from all pages"""
        print(f"Starting to scrape job links from {max_pages} pages...")
        
        for page_num in range(1, max_pages + 1):
            try:
                url = self.get_next_page_url(page_num)
                print(f"\n[Page {page_num}/{max_pages}] Accessing: {url}")
                
                self.driver.get(url)
                time.sleep(2)  # Polite delay
                
                # Extract job links from this page
                links_found = self.extract_job_links_from_page()
                print(f"  Total links found on this page: {links_found}")
                print(f"  Total unique links collected so far: {len(self.job_links)}")
                
            except Exception as e:
                print(f"Error on page {page_num}: {e}")
                continue
        
        print(f"\n✓ Finished collecting job links. Total: {len(self.job_links)}")
        return self.job_links
    
    def extract_job_details(self, job_url):
        """Extract detailed information from individual job page"""
        job_info = {
            'Job Link': job_url,
            'Company Name': '',
            'Address': '',
            'Website': '',
            'Contact Person': '',
            'Email': '',
            'Phone': '',
            'Fax': ''
        }
        
        try:
            self.driver.get(job_url)
            time.sleep(1.5)
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Extract Company Name
            company_elem = soup.find('h1') or soup.find('div', class_=re.compile(r'company|firma'))
            if company_elem:
                job_info['Company Name'] = company_elem.get_text(strip=True)
            
            # Look for contact information in various formats
            # Method 1: Find all text and search for patterns
            page_text = soup.get_text()
            
            # Extract Email
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            emails = re.findall(email_pattern, page_text)
            if emails:
                job_info['Email'] = emails[0]
            
            # Extract Phone (German format)
            phone_pattern = r'(?:Tel\.|Telefon|Phone|Tel|Fon)[\s:]*([+\d\s\(\)\-\/]{8,})'
            phone_match = re.search(phone_pattern, page_text, re.IGNORECASE)
            if phone_match:
                job_info['Phone'] = phone_match.group(1).strip()
            
            # Extract Fax
            fax_pattern = r'(?:Fax)[\s:]*([+\d\s\(\)\-\/]{8,})'
            fax_match = re.search(fax_pattern, page_text, re.IGNORECASE)
            if fax_match:
                job_info['Fax'] = fax_match.group(1).strip()
            
            # Method 2: Look for structured data
            # Find contact information blocks
            contact_divs = soup.find_all(['div', 'p', 'td'], text=re.compile(r'Kontakt|Ansprechpartner', re.IGNORECASE))
            
            for div in contact_divs:
                parent = div.find_parent()
                if parent:
                    text = parent.get_text()
                    
                    # Extract contact person
                    person_pattern = r'Ansprechpartner[\s:]*([A-ZÄÖÜ][a-zäöüß]+(?:\s[A-ZÄÖÜ][a-zäöüß]+)+)'
                    person_match = re.search(person_pattern, text)
                    if person_match and not job_info['Contact Person']:
                        job_info['Contact Person'] = person_match.group(1).strip()
            
            # Extract Website/Homepage
            website_links = soup.find_all('a', href=re.compile(r'^https?://(?!www\.truckerboerse\.net)'))
            for link in website_links:
                href = link.get('href', '')
                if href and ('mailto:' not in href):
                    job_info['Website'] = href
                    break
            
            # Extract Address
            # Look for postal code and city patterns (German format)
            address_pattern = r'\b\d{5}\s+[A-ZÄÖÜ][a-zäöüß]+(?:\s[A-ZÄÖÜ][a-zäöüß]+)*\b'
            address_match = re.search(address_pattern, page_text)
            if address_match:
                # Try to get street as well
                full_address_pattern = r'([A-ZÄÖÜ][a-zäöüß]+(?:straße|str\.|weg|platz|allee)?\s+\d+[a-z]?)[,\s]+' + address_pattern
                full_match = re.search(full_address_pattern, page_text, re.IGNORECASE)
                if full_match:
                    job_info['Address'] = full_match.group(0).strip()
                else:
                    job_info['Address'] = address_match.group(0).strip()
            
            # Alternative: Look for address in structured format
            address_elems = soup.find_all(text=re.compile(r'\d{5}'))
            for elem in address_elems:
                text = elem.strip()
                if len(text) > 5 and len(text) < 100:
                    job_info['Address'] = text
                    break
            
        except Exception as e:
            print(f"  Error extracting details from {job_url}: {e}")
        
        return job_info
    
    def scrape_all_job_details(self):
        """Visit each job link and extract detailed information"""
        print(f"\nStarting to scrape details from {len(self.job_links)} job postings...")
        
        for index, job_url in enumerate(self.job_links, 1):
            try:
                print(f"\n[{index}/{len(self.job_links)}] Scraping: {job_url}")
                job_data = self.extract_job_details(job_url)
                self.job_data.append(job_data)
                
                # Display extracted data
                print(f"  Company: {job_data['Company Name']}")
                print(f"  Email: {job_data['Email']}")
                print(f"  Phone: {job_data['Phone']}")
                
                # Polite delay between requests
                time.sleep(1.5)
                
            except Exception as e:
                print(f"  Failed to scrape {job_url}: {e}")
                continue
        
        print(f"\n✓ Finished scraping all job details!")
        return self.job_data
    
    def save_to_excel(self, filename=None):
        """Save scraped data to Excel file"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'truckerboerse_jobs_{timestamp}.xlsx'
        
        df = pd.DataFrame(self.job_data)
        
        # Reorder columns
        column_order = ['Job Link', 'Company Name', 'Address', 'Website', 
                       'Contact Person', 'Email', 'Phone', 'Fax']
        df = df[column_order]
        
        # Save to Excel
        df.to_excel(filename, index=False, engine='openpyxl')
        print(f"\n✓ Data saved to: {filename}")
        print(f"  Total jobs scraped: {len(self.job_data)}")
        
        return filename
    
    def run(self, max_pages=258, save_file=True):
        """Main execution method"""
        try:
            print("="*60)
            print("TruckerBoerse.net Job Scraper")
            print("="*60)
            
            # Step 1: Collect all job links
            self.scrape_all_pages(max_pages)
            
            # Step 2: Scrape details from each job
            self.scrape_all_job_details()
            
            # Step 3: Save to Excel
            if save_file:
                self.save_to_excel()
            
            print("\n" + "="*60)
            print("SCRAPING COMPLETED SUCCESSFULLY!")
            print("="*60)
            
        except Exception as e:
            print(f"\nFatal error: {e}")
        finally:
            self.close()
    
    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()
            print("\nBrowser closed.")


# Example usage
if __name__ == "__main__":
    # Initialize scraper
    scraper = TruckerBoerseJobScraper(headless=False)  # Set to True for headless mode
    
    # Run the scraper
    # For testing, use max_pages=2
    # For full scrape, use max_pages=258
    scraper.run(max_pages=2, save_file=True)