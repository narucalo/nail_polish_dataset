from web_locator import WebElementLocator, LocatorType, webdriver_context
from image_processor import NailPolishImageProcessor

def main():
    url = "https://dtknailsupply.com/collections/opi-nail-lacquer"

    with webdriver_context(incognito=True) as driver:  # Launch in incognito mode
        locator = WebElementLocator(driver)
        locator.start(url)

        # Define the locator for the OPI images
        target_locator = (LocatorType.XPATH, "//img[contains(@alt, 'OPI Nail Lacquer')]")

        # Find all OPI images on the page
        opi_images = locator.wait_for_elements(*target_locator)

        if opi_images:
            html_content_list = locator.get_html_content(opi_images)

            processor = NailPolishImageProcessor('nail_polish_dataset.csv', 'images')
            processor.process(html_content_list)
        else:
            print("No OPI images found on the page.")

if __name__ == "__main__":
    main()
