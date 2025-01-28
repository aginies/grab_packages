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

def download_file(file_url, file_path, thread_id):
    """
    Downloads a single file with a progress bar.
    """
    try:
        with urllib.request.urlopen(file_url, context=ssl.create_default_context()) as response:
            file_size = int(response.info().get('Content-Length', 0))
            block_size = 8192
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
        out_file.flush()
        print(f"Thread {thread_id}: {type(e).__name__} occurred: {e}")


def split_version(version):
    # Split the version string into parts based on changes in character types (digits vs. letters)
    return re.findall(r'[a-z]+|\d+', version)

def get_latest_version(versions):
    return max(versions, key=lambda v: split_version(v))

def get_build_tuple(package, url):
    build_str = url.split(package)[-1].split('.src')[0]

    # Split on non-digit characters (e.g., hyphens)
    parts = [part for part in build_str.replace('-', '').split('.') if part.isdigit()]

    return tuple(map(int, parts))

def find_latest_version(package_version, product_name, product_packages):
    for package, details in package_version.items():
        versions = details.get('versions', set())
        urls = details.get('urls', set())
        #print(f"FLV {package}: {versions} {urls}")
        latest_version = get_latest_version(versions)
        #print(f"FLV {product_name}: Latest version of {package} is {latest_version}")
        if package not in product_packages:
            product_packages[package] = { 'versions': set(), 'urls': set() }

        sorted_urls = sorted(urls, key=lambda x: get_build_tuple(package, x), reverse=True)
        latest_url = sorted_urls[0]
        print("Latest URL:", latest_url)
        product_packages[package]['versions'] = latest_version
        product_packages[package]['urls'] = latest_url

    return product_packages

def download_latest_version(product_packages, product_name, product_dir):
    # Create a ThreadPoolExecutor with a maximum of 5 worker threads
    with ThreadPoolExecutor(max_workers=5) as executor:
        thread_id = 1  # Initialize thread ID counter

        for package, details in product_packages.items():
            #print("DEBUG", package)
            versions = details.get('versions', set())
            urls = details.get('urls', set())
            #print("DL", urls, versions)
            #for url in urls:
            file_name = os.path.basename(urls)
            file_path = os.path.join(product_dir, file_name)

            if os.path.exists(file_path):
                print(f"File {file_name} already exists in {product_name}. Skipping download.")
                continue

            print(urls, file_path, thread_id)
            executor.submit(download_file, urls, file_path, thread_id)
            thread_id += 1

def grab_files(config):
    """
    Grabs all files from an HTTPS server that match patterns from a file and end with 'src.rpm',
    Returns:
        None
    """
    try:
        # Read configuration
        server_url = config.get('server', 'url')
        paths_template = config.get('server', 'paths')
        pathsSLFO_template = config.get('server', 'pathsSLFO')
        packages_file = config.get('files', 'packages')
        product_names = config.get('products', 'product_names').split(',')
        store_path = config.get('store', 'path')

        # Read patterns from the packages_file
        with open(packages_file, 'r') as f:
            patterns = [line.strip() for line in f]
        patterns = [line for line in patterns if line]  # Remove empty lines

        # Clear the screen at the beginning
        os.system('clear')

        for product_name in product_names:
            product_name = product_name.strip()
            print(f"Working on product: {product_name}")
            # Determine the correct path template based on product name
            if not re.match(r'SLE-1[2-5]-SP\d+', product_name):
                paths_template = pathsSLFO_template

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
                    #print(links)
                    product_packages = []
                    package_version = {}
                    package_url = None
                    name_part = ""
                    version_part = ""
                    extra_part = ""
                    if links:
                        product_packages = {}
                        latest_versions = {}  # Store latest versions of each package
                        for file_name in links:
                            # Remove everything after '<' if it exists
                            file_name = file_name.split('<')[0]
                            #print("Working on:", file_name)
                            # Check if the filename matches any pattern AND ends with "src.rpm"
                            for pattern in patterns:
                                if pattern in file_name and file_name.endswith("src.rpm"):
                                    #print("DEBUG pattern match src.rpm", pattern)
                                    parts = file_name.split('-')
                                    second_last_part = parts[-2]
                                    # Check if the last part is a number
                                    if parts and len(parts[-1]) > 0 and second_last_part[0].isdigit():
                                        name_part_s = '-'.join(parts[:-2])
                                        name_part = (name_part_s.lstrip('.')).lstrip('/')
                                        # The pre-last part is the version number
                                        version_part = ''.join(parts[-2])
                                        extra_part = ''.join(parts[-1])
                                        if name_part not in package_version:
                                            package_version[name_part] = { 'versions': set(), 'urls': set() }

                                        #print("DEBUG:", name_part)
                                        package_url = url+"/"+name_part+"-"+version_part+"-"+extra_part
                                        package_version[name_part]['versions'].add(version_part)
                                        package_version[name_part]['urls'].add(package_url)
                                    else:
                                        print(f"Sounds like a BUG for {parts}")

                        product_packages = find_latest_version(package_version, product_name, product_packages)
                        #print(product_packages)
                        download_latest_version(product_packages, product_name, product_dir)

                except urllib.error.HTTPError as e:
                    if e.code == 404:
                        print(f"HTTP Error 404 for path {path}: Not Found")
                    else:
                        print(f"HTTP Error for path {path}: {e.code} - {e.reason}")
                        if hasattr(e, 'read'):
                            print(e.read().decode('utf-8'))

    except Exception as e:
        print(f"An error occurred: {e}")


config = configparser.ConfigParser()
config.read('config.ini')
grab_files(config)
