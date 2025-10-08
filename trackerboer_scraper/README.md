# Amazon Product Scraper

A Python web scraper that extracts product information from Amazon search results using Selenium WebDriver and BeautifulSoup.

## Features

- 🔍 Scrapes product details from Amazon search results
- 📊 Extracts: Product name, price, rating, review count, and URL
- 🤖 Uses Microsoft Edge WebDriver for automation
- 📁 Exports data to CSV format
- 🛡️ Includes anti-detection measures
- ⏱️ Polite scraping with delays between requests

## Prerequisites

- Python 3.7+
- Microsoft Edge browser installed
- Microsoft Edge WebDriver (msedgedriver.exe)

## Installation

1. **Clone or download this project**

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv .venv
   ```

3. **Activate the virtual environment**
   - Windows:
     ```bash
     .venv\Scripts\activate
     ```
   - Linux/Mac:
     ```bash
     source .venv/bin/activate
     ```

4. **Install required packages**
   ```bash
   pip install selenium beautifulsoup4
   ```

5. **Download Microsoft Edge WebDriver**
   - Visit: https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/
   - Download the version matching your Edge browser version
   - Extract `msedgedriver.exe` to `C:\EdgeDriver\` (or update the path in the code)

## Project Structure

```
project/
│
├── scraper.py          # Main scraper script
├── results.csv         # Output file (generated after running)
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Usage

1. **Run the scraper**
   ```bash
   python scraper.py
   ```

2. **Customize the search term**
   Edit the last line in `scraper.py`:
   ```python
   if __name__ == '__main__':
       main('ultrawide monitor')  # Change search term here
   ```

3. **View results**
   Open `results.csv` in Excel or any spreadsheet application

## Configuration

### Change the number of pages to scrape

In the `main()` function, modify the range:
```python
for page in range(1, 21):  # Change 21 to scrape more/fewer pages
```

### Enable headless mode (run without opening browser)

Uncomment this line in `main()`:
```python
options.add_argument('--headless=new')
```

### Change the Edge WebDriver path

Update this line if you placed the driver elsewhere:
```python
service = Service(r'C:\EdgeDriver\msedgedriver.exe')
```

## Output Format

The scraper generates a CSV file with the following columns:

| Column | Description |
|--------|-------------|
| Description | Product name/title |
| Price | Product price (e.g., $299.99) |
| Rating | Star rating (e.g., 4.5 out of 5 stars) |
| ReviewCount | Number of reviews (e.g., (965)) |
| Url | Direct link to product page |

## Important Notes

⚠️ **Legal and Ethical Considerations:**
- This scraper is for educational purposes only
- Amazon's Terms of Service prohibit automated scraping
- Respect Amazon's `robots.txt` and rate limits
- Consider using Amazon's official Product Advertising API for production use
- Add appropriate delays between requests to avoid overloading servers

⚠️ **Anti-Bot Measures:**
- Amazon may detect and block automated scrapers
- You may encounter CAPTCHAs or IP blocks
- Consider using proxies or VPNs for extensive scraping
- Rotate user agents and implement random delays

## Troubleshooting

### Issue: "msedgedriver executable needs to be in PATH"
**Solution:** Download msedgedriver and update the path in the code

### Issue: "AttributeError" or no products found
**Solution:** Amazon's HTML structure may have changed. Check the HTML selectors in `extract_record()`

### Issue: Getting 0 results
**Solution:** 
- Check if Amazon is showing a CAPTCHA
- Increase the `time.sleep()` value
- Verify your internet connection
- Try running without headless mode to see what's happening

### Issue: SSL or connection errors
**Solution:** Check your internet connection and firewall settings

## Dependencies

```
selenium>=4.0.0
beautifulsoup4>=4.9.0
```

Create a `requirements.txt`:
```bash
pip freeze > requirements.txt
```

## Upgrade Guide

If you have an older version using `msedge-selenium-tools`:

1. Uninstall old package:
   ```bash
   pip uninstall msedge-selenium-tools
   ```

2. Install new packages:
   ```bash
   pip install --upgrade selenium beautifulsoup4
   ```

3. The code in this repository already uses the modern Selenium 4 syntax

## Future Improvements

- [ ] Add proxy support
- [ ] Implement CAPTCHA handling
- [ ] Add database storage (SQLite/PostgreSQL)
- [ ] Create CLI with arguments for search terms
- [ ] Add logging functionality
- [ ] Implement retry logic for failed requests
- [ ] Add support for filtering by price, rating, etc.
- [ ] Multi-threading for faster scraping

## Contributing

Feel free to fork this project and submit pull requests for improvements!

## License

This project is for educational purposes only. Use at your own risk.

## Disclaimer

This tool is provided as-is for educational purposes. The author is not responsible for any misuse or violations of Amazon's Terms of Service. Always check and comply with the website's terms of service and robots.txt before scraping.

---

**Happy Scraping! 🚀**

For issues or questions, please open an issue on the repository.