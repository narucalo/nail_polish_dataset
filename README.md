Nail Polish Dataset Project
This project is designed to scrape product information and images of nail polishes from the website https://dtknailsupply.com/collections/opi-nail-lacquer using Selenium for web automation and BeautifulSoup for HTML parsing. The extracted data is then stored in a CSV file for further analysis or use.

Project Structure
main.py: The main entry point of the project.
web_locator.py: Contains the WebElementLocator class for interacting with the webpage using Selenium.
image_processor.py: Contains the ImageProcessor and NailPolishImageProcessor classes for processing image elements and saving data.
Dependencies
Python 3.x
Selenium
BeautifulSoup4
pandas
requests
You can install these dependencies using pip:

Bash
pip install selenium beautifulsoup4 pandas requests
Use code with caution.

How to Run
Make sure you have a ChromeDriver compatible with your Chrome browser version. You can download it from https://chromedriver.chromium.org/downloads.
Place the ChromeDriver executable in your system's PATH or provide its path when initializing the WebDriver in web_locator.py.
Run the script:
Bash
python main.py
Use code with caution.

Functionality
Web Scraping:

The WebElementLocator class in web_locator.py handles the interaction with the webpage.
It navigates to the target URL, locates the relevant image elements, and extracts their HTML content.
Image Processing:

The NailPolishImageProcessor class in image_processor.py processes the extracted HTML content.
It uses BeautifulSoup to parse the HTML, extracts product information (name, description) from image alt attributes, and downloads the images.
It also handles potential errors during information extraction and image downloading.
Data Storage:

The extracted data, including image filenames, product names, and descriptions, is stored in a CSV file named nail_polish_dataset.csv.
The script checks for and removes duplicates in the dataset to maintain data integrity.
Customization
Target Website: You can modify the url variable in main.py to scrape a different webpage.
Locators: Adjust the XPath expressions in main.py ( target_locator and sibling_locator) to match the specific structure of the webpage you're targeting.
Information Extraction: Customize the extract_info method in NailPolishImageProcessor if the HTML structure or the way product information is embedded in image elements is different on your target website.

graph LR
    subgraph main.py
        A[Start] --> B[Initialize WebElementLocator]
        B --> C[Navigate to URL]
        C --> D[Find OPI Images]
        D --> E{OPI Images Found?}
        E -->|Yes| F[Extract HTML Content]
        E -->|No| G[Log "No OPI images found"]
        F --> H[Initialize NailPolishImageProcessor]
        H --> I[Process HTML Content]
        I --> J[End]
        G --> J
    end
    
    subgraph web_locator.py
        B[Initialize WebElementLocator] --> C[Navigate to URL]
        C --> D[Find OPI Images]
        D --> E
        F[Extract HTML Content] --> I
    end

    subgraph image_processor.py
        H[Initialize NailPolishImageProcessor]
        I[Process HTML Content] --> K[Extract Info from HTML]
        K --> L[Download Image]
        L --> M[Update Dataset]
        M --> I
    end