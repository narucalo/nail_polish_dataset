from abc import ABC, abstractmethod
import requests
import pandas as pd
import os
from bs4 import BeautifulSoup
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ImageProcessor(ABC):
    def __init__(self, dataset_path: str, images_dir: str):
        self.dataset_path = dataset_path
        self.images_dir = images_dir
        os.makedirs(images_dir, exist_ok=True)

        # Remove duplicates from the existing dataset (if it exists)
        if os.path.exists(self.dataset_path):
            df = pd.read_csv(self.dataset_path)
            df.drop_duplicates(subset=['filename'], keep='first', inplace=True)
            df.to_csv(self.dataset_path, index=False)
            logging.info("Removed duplicates from the existing dataset")

    @abstractmethod
    def extract_info(self, img_element_str: str) -> tuple:
        """Extracts information from an image element string"""
        pass

    def download_image(self, src: str, filename: str) -> None:
        """Downloads an image from the given source and saves it to the images directory."""
        max_retries = 3
        image_path = os.path.join(self.images_dir, filename)
        for attempt in range(1, max_retries + 1):
            try:
                response = requests.get(src, timeout=10, stream=True)
                response.raise_for_status()
                with open(image_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                logging.info(f"Downloaded {filename} to {image_path}")
                break
            except requests.exceptions.RequestException as e:
                if attempt < max_retries:
                    logging.warning(f"Error downloading image (attempt {attempt}/{max_retries}): {e}. Retrying...")
                else:
                    logging.error(f"Failed to download image after {max_retries} attempts: {filename}")
                    logging.error(f"URL: {src}")  # Include the URL in the error log

    def update_dataset(self, filename: str, product_name: str, description: str) -> None:
        """Appends new information directly to the CSV file"""
        new_entry = pd.DataFrame([{"filename": filename, "product_name": product_name, "description": description}])

        # Append directly to the CSV file
        new_entry.to_csv(self.dataset_path, mode='a', header= not os.path.exists(self.dataset_path), index=False)
        logging.info(f"Updated dataset with {filename}")

class NailPolishImageProcessor(ImageProcessor):
    def __init__(self, dataset_path, images_dir):
        super().__init__(dataset_path, images_dir)  # Call the parent constructor once

    def extract_info(self, img_element_str: str) -> tuple:
        """Extracts information from an image element string for nail polish products"""
        try:
            soup = BeautifulSoup(img_element_str, 'html.parser')
            img_tag = soup.find('img')
            if not img_tag:
                raise ValueError("No 'img' tag found in the input")

            src = img_tag.get('src')
            alt = img_tag.get('alt')
            if not src or not alt:
                raise AttributeError("Missing 'src' or 'alt' attribute in the 'img' tag")

            filename = os.path.basename(src).split('?')[0]
            src = 'https:' + src if src.startswith('//') else src
            product_name, _, description = alt.partition('-')
            product_name = product_name.strip()

            # Remove "sold by DTK Nail Supply" from the description
            description = description.replace("sold by DTK Nail Supply", "").strip()

            return filename, src, product_name, description
        except (ValueError, AttributeError) as e:
            logging.warning(f"Error extracting information: {e}. Skipping this image element.")
            return None


    def process_and_download(self, img_element_str: str) -> None:
        """Processes an image element string, downloads the image, and updates the dataset"""
        info = self.extract_info(img_element_str)
        if info:
            filename, src, product_name, description = info
            self.download_image(src, filename)
            self.update_dataset(filename, product_name, description)

    def process(self, html_content_list: list) -> None:
        """Processes a list of HTML content strings, extracts information, downloads images, and updates the dataset"""
        for html_content in html_content_list:
            self.process_and_download(html_content)