#!/usr/bin/python3
# 01/2025
# aginies@suse.com
import ssl
import urllib.request
import re
import configparser
import os
import threading
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
from packaging import version

def download_file(file_url, file_path, thread_id):
    """
    Downloads a single file with a progress bar.
    """
    try:
        with urllib.request.urlopen(file_url, context=ssl.create_default_context()) as response:
            file_size = int(response.info().get('Content-Length', 0))
            block_size = 8192

            # Extract filename from file_path
            file_name = os.path.basename(file_path)

            # Create a tqdm progress bar
            progress_bar = tqdm(total=file_size, unit='B', unit_scale=True,
                                desc=f"{file_name}",
                                position=thread_id, leave=True)

            with open(file_path, 'wb') as out_file:
                for data in iter(lambda: response.read(block_size), b""):
                    out_file.write(data)
                    out_file.flush()
                    progress_bar.update(len(data))

            progress_bar.close()
            #print(f"Thread {thread_id}: {file_name} - Downloaded")

            os.system('clear')

    except urllib.error.HTTPError as e:
        print(f"Thread {thread_id}: Error downloading {file_url}: {e.code} - {e.reason}")
    except (KeyboardInterrupt, Exception) as e:
        print(f"Thread {thread_id}: Download interrupted. Attempting to save progress...")
        out_file.flush()  # Try to save what's been downloaded so far
        print(f"Thread {thread_id}: {type(e).__name__} occurred: {e}")

def grab_files(config):
    """
    Grabs all files from an HTTPS server that match patterns from a file and end with 'src.rpm',
    showing download progress. Handles multiple paths from the config file, dynamically generated
    using product names. Stores downloaded files in product-specific directories.
    Skips downloading if the file already exists. Suppresses detailed error logs for 404 errors.
    Uses a ThreadPoolExecutor to limit the number of concurrent downloads to 5.
    Args:
        config: A configparser.ConfigParser object containing the server URL, paths, and package file name.

    Returns:
        None
    """

    try:
        # Read configuration
        server_url = config.get('server', 'url')
        paths_template = config.get('server', 'paths')
        packages_file = config.get('files', 'packages')
        product_names = config.get('products', 'product_names').split(',')
        store_path = config.get('store', 'path')

        # Read patterns from the packages_file
        with open(packages_file, 'r') as f:
            patterns = [line.strip() for line in f]

        # Clear the screen at the beginning
        os.system('clear')

        # Create a ThreadPoolExecutor with a maximum of 5 worker threads
        with ThreadPoolExecutor(max_workers=5) as executor: 
            thread_id = 1  # Initialize thread ID counter

            for product_name in product_names:
                product_name = product_name.strip()

                # Create directory for the product
                product_dir = os.path.join(store_path, product_name)
                os.makedirs(product_dir, exist_ok=True)

                # Generate paths dynamically using product names and the template
                paths = [p.strip().replace('{product_name}', product_name) for p in paths_template.split(',')]

                for path in paths:
                    url = f"{server_url}/{path}"
                    #print(f"Checking path: {url}")

                    try:
                        with urllib.request.urlopen(url, context=ssl.create_default_context()) as response:
                            html = response.read().decode('utf-8')

                        # Find all <a> tags with href attributes
                        links = re.findall(r'<a href="([^"]+)"', html)

                        if links:
                            latest_versions = {}  # Store latest versions of each package
                            for file_name in links:
                                # Remove everything after '<' if it exists
                                file_name = file_name.split('<')[0]
                                # Check if the filename matches any pattern AND ends with "src.rpm"
                                for pattern in patterns:
                                     if pattern in file_name and file_name.endswith("src.rpm"):
                                        # Extract version from filename (assuming format like 'package-1.2.3-4.src.rpm')
                                        version_str = re.search(r'-(.*?)-', file_name).group(1)
                                        package_name = file_name.split('-')[0]

                                        # Check if this is the latest version of the package
                                        if package_name not in latest_versions or version.parse(version_str) > version.parse(latest_versions[package_name][0]):
                                            latest_versions[package_name] = (version_str, file_name)

                            # Download only the latest versions
                            for version_str, file_name in latest_versions.values():
                                file_url = url + '/' + file_name
                                file_path = os.path.join(product_dir, file_name)

                                #if os.path.exists(file_path):
                                #    print(f"File {file_name} already exists in {product_name}. Skipping download.")
                                #    continue

                                #print(f"Attempting to download: {file_url}")
                                executor.submit(download_file, file_url, file_path, thread_id)
                                thread_id += 1  # Increment thread ID

                        else:
                            print("No matching files found on the server.")

                    except urllib.error.HTTPError as e:
                        if e.code == 404:
                            print(f"HTTP Error 404 for path {path}: Not Found")  # Suppressed detailed log
                        else:
                            print(f"HTTP Error for path {path}: {e.code} - {e.reason}")
                            if hasattr(e, 'read'):
                                print(e.read().decode('utf-8'))

    except Exception as e:
        print(f"An error occurred: {e}")


config = configparser.ConfigParser()
config.read('config.ini')

grab_files(config)
