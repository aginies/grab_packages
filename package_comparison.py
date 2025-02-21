import configparser
import os
import re
import subprocess
from datetime import datetime

# Read config.ini
config = configparser.ConfigParser()
config.read('config.ini')

PRODUCTS = config['products']['product_names'].split(', ')
STORE_PATH = config['store']['path']
PACKAGE_EXTENSION = "src.rpm"

resultdir = f"{os.getcwd()}/results"
result = os.path.join(resultdir, 'index.html')
product_diff = os.path.join(resultdir, 'diffs')

# Create directories
os.makedirs(resultdir, exist_ok=True)
os.makedirs(product_diff, exist_ok=True)

# Set date
now = datetime.now()
date_str = now.strftime("%Y/%m/%d %H:%M")

def usage():
    print("""
Purpose:
This script compares SRPM versions of packages across multiple SUSE distributions.
It generates an HTML report with links to changelog and RPM diffs.

Usage:
python3 package_compare.py <result_dir> <package_list>

Arguments:
- result_dir: Path where results will be stored
- package_list: File containing list of packages to compare

The script uses configuration from config.ini for product names and paths.
""")
    exit(1)

def get_packages(package_file):
    with open(package_file, 'r') as f:
        return [line.strip() for line in f if line.strip()]

def find_rpm_files2(package_name, store_path):
    rpm_files = []
    for root, _, files in os.walk(store_path):
        for file in files:
            if (file.endswith(f".{PACKAGE_EXTENSION}") and file.startswith(f"{package_name}-")):
                rpm_files.append(os.path.join(root, file))
    return rpm_files

def find_rpm_files(package_name, store_path):
    rpm_files = []
    for product in PRODUCTS:
        cmd = f"ls -t -1 {os.path.join(store_path, product)}/{package_name}*.src.rpm"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            rpm_files.append(result.stdout.strip().split('\n')[0])  # Get the latest version
    return rpm_files

def get_product_rpm(product, store_path, rpm_files):
    product_dir = os.path.join(store_path, product)
    for rpm in rpm_files:
        if rpm.startswith(os.path.join(product_dir, "")):
            return rpm
    return None

def rpm_info(package_path):
    cmd = f"rpm -qp --qf '%{{name}} %{{version}} %{{release}}' {package_path}"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        parts = result.stdout.strip().split()
        return (parts[0], parts[1], parts[2])  # Now returns name, version, release
    else:
        return None

def diff_changelog(package_a, package_b, diff_file):
    tmpdir = "/tmp"
    temp_file = os.path.join(tmpdir, f'tmp-chlog-{os.getpid()}')

    cmd = f"rpm -qp --changelog {package_a} > {temp_file} && rpm -qp --changelog {package_b} >> {temp_file}"
    subprocess.run(cmd, shell=True)

    # Replace bugzilla, fate, jsc links
    with open(temp_file, 'r') as f:
        lines = []
        for line in f:
            modified_line = line
            modified_line = re.sub(r'(http://|https://[^ ]+)', r'<a href="\1">\1</a>', modified_line)
            modified_line = re.sub(r'jsc#([A-Z]+-\d+)', r'<a href="https://jira.suse.com/browse/\1" target="_blank">jsc#\1</a>', modified_line)
            modified_line = re.sub(r'FATE#(\d+)', r'<a href="https://fate.suse.com/\1">FATE#\1</a>', modified_line)
            modified_line = re.sub(r'bsc#(\d+)', r'<a href="https://bugzilla.suse.com/show_bug.cgi?id=\1" target="_blank">bsc#\1</a>', modified_line)
            modified_line = re.sub(r'boo#(\d+)', r'<a href="https://bugzilla.suse.com/show_bug.cgi?id=\1" target="_blank">boo#\1</a>', modified_line)
            modified_line = re.sub(r'CVE-(\d+-\d+)', r'<a href="https://www.suse.com/security/cve/CVE-\1.html" target="_blank">CVE-\1</a>', modified_line)
            lines.append(modified_line)
    
    with open(diff_file, 'w') as f:
        f.write("<html><pre>\n")
        f.writelines(lines)
        f.write("</pre></html>")

    os.remove(temp_file)

def main():
    if len(sys.argv) != 3:
        usage()

    resultdir = sys.argv[1]
    package_list = sys.argv[2]

    global result
    result = os.path.join(resultdir, 'index.html')
    product_diff = os.path.join(resultdir, 'diffs')

    # Clean and create directories
    os.makedirs(product_diff, exist_ok=True)

    packages = get_packages(package_list)

    with open(result, 'w') as f:
        f.write(f"<html>\n<head><title>Package Comparison ({datetime.now().strftime('%Y/%m/%d %H:%M')})</title></head>\n")
        f.write("<style>")
        f.write("th.package-info, td.package-info { width: 250px; }")
        f.write(".styled-table {\n")
        f.write("border-collapse: collapse;\n")
        f.write("margin: 25px 0;\n")
        f.write("font-size: 0.9em;\n")
        f.write("font-family: sans-serif;\n")
        f.write("min-width: 400px;\n")
        f.write("box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);\n")
        f.write("}\n")
        f.write(".styled-table thead tr {\n")
        f.write("background-color: #009879;\n")
        f.write("color: #ffffff;\n")
        f.write("text-align: left;\n")
        f.write("}\n")
        f.write(".styled-table th,\n")
        f.write(".styled-table td {\n")
        f.write("padding: 12px 15px;\n")
        f.write("}\n")
        f.write(".styled-table tbody tr {\n")
        f.write("border-bottom: 1px solid #dddddd;\n")
        f.write("}\n")
        f.write(".styled-table tbody tr:nth-of-type(even) {\n")
        f.write("background-color: #f3f3f3;\n")
        f.write("}\n")
        f.write(".styled-table tbody tr:last-of-type {\n")
        f.write("border-bottom: 2px solid #009879;\n")
        f.write("}\n")
        f.write(".styled-table tbody tr.active-row {\n")
        f.write("font-weight: bold;\n")
        f.write("color: #009879;\n")
        f.write("}\n")
        f.write("div{")
        f.write("font-size: 2rem;")
        f.write("text-align: left;")
        f.write("height:5vh;")
        f.write("line-height: 5vh;")
        f.write("color: #fcedd8;")
        f.write("background: green;")
        f.write("font-family: 'Niconne', cursive;")
        f.write("font-weight: 700;")
        f.write("}")
        f.write("</style>")
        f.write("<div>SRPM Packages versions comparison</div>\n")
        f.write(f"<p>Based on src.rpm, diff done on {os.uname().machine}</p>\n")
        f.write("<table class='styled-table'>\n<tr><th class='package-info'></th>")

    for product in PRODUCTS:
        with open(result, 'a') as f:
            f.write(f"<th>{product}</th>")

    with open(result, 'a') as f:
        f.write("</tr>\n<tr>")

    for package in packages:
        current_pkg = None
        prev_pkg = None
        prev_product = None
        with open(result, 'a') as f:
                f.write("<tr>")  # Start a new row for each package

        print(f"Processing {package}")

        try:
            # Find all RPM files for this package
            rpm_files = find_rpm_files(package, STORE_PATH)
            print(f"searching {package} | FOUND: {rpm_files}")

            with open(result, 'a') as f:
                f.write("<td class='package-info' bgcolor='#e5e5e5'>")

            # Get URL and summary using the first RPM file found
            if rpm_files:
                sample_rpm = rpm_files[0]
                url_cmd = f"rpm -qp --qf '%{{url}} %{{summary}}' {sample_rpm}"
                url_result = subprocess.run(url_cmd, shell=True, capture_output=True, text=True)

                if url_result.returncode == 0:
                    parts = url_result.stdout.strip().split(maxsplit=1)  # Split only once
                    url = parts[0] if len(parts) > 0 else ''
                    summary = parts[1] if len(parts) > 1 else ''

                    with open(result, 'a') as f:
                        f.write(f"<a href='{url}'>{package}</a><br>{summary}")
                else:
                    with open(result, 'a') as f:
                        f.write(package)
            else:
                with open(result, 'a') as f:
                    f.write(f"{package} (No RPM files found)")

            with open(result, 'a') as f:
                f.write("</td>\n")

                for product in PRODUCTS:
                    print(product)
                    rpm_a = None

                    # Find RPM for the current product
                    rpm_a = get_product_rpm(product, STORE_PATH, rpm_files)
                    #print("Package current product: ", rpm_a)

                    if rpm_a and os.path.exists(rpm_a):
                        nameA, versionA, releaseA = rpm_info(rpm_a)

                        with open(result, 'a') as f:
                            f.write(f"<td align='center'><b>{versionA}-{releaseA}</b>")

                        for other_product in PRODUCTS:
                            if other_product == product:
                                continue  # Skip comparison with itself

                            rpm_b = get_product_rpm(other_product, STORE_PATH, rpm_files)
                            #print("Package other product:", rpm_b)

                            if rpm_b and os.path.exists(rpm_b):
                                nameB, versionB, releaseB = rpm_info(rpm_b)
                                diff_file = os.path.join(product_diff, f"chlog_{product}_{nameA}_{versionA}-{releaseA}_VS_{other_product}_{nameB}_{versionB}-{releaseB}.html")
                                if os.path.exists(diff_file):
                                    print(f"{diff_file} already exist")
                                else:
                                    diff_changelog(rpm_a, rpm_b, diff_file)

                                if os.path.exists(diff_file):
                                    with open(result, 'a') as f:
                                        f.write(f"<br><a href='diffs/{os.path.basename(diff_file)}' style='color:green;><font size='2'>Chglog Diff {other_product}</font></a>")
                                        # Add RPM diff if applicable
                                        rpm_diff_cmd = "/home/aginies/devel/github/aginies/grab_packages/rpmdiff"
                                        full_diff = os.path.join(product_diff, f"rpmdiff_{product}_{nameA}_{versionA}-{releaseA}_VS_{other_product}_{nameB}_{versionB}-{releaseB}.txt")
                                        if not os.path.exists(full_diff):
                                            subprocess.run(f"{rpm_diff_cmd} {rpm_a} {rpm_b} > {full_diff}", shell=True)
                                        f.write(f"<br><a href='diffs/{os.path.basename(full_diff)}' style='color:purple;><font size='2'>Diff {other_product}</font></a>")
                                else:
                                    with open(result, 'a') as f:
                                        f.write("<br><font color='red'>No changelog diff</font>")

                        with open(result, 'a') as f:
                            f.write("</td>\n")
                    else:
                        with open(result, 'a') as f:
                            f.write("<td align='center'><font color='red'>Not present</font></td>\n")

        except Exception as e:
            print(f"Error processing {package}: {e}")
            with open(result, 'a') as f:
                f.write(f"<td align='center' style='background-color: #ffe6e6;'>{str(e)}</td>\n")

    with open(result, 'a') as f:
        f.write("</tr></table>\n<hr><small><a href='https://github.com/aginies/grab_packages'>Generated by package_compare.py</a></small></html>")

if __name__ == "__main__":
    import sys
    main()
