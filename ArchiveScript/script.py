#!/usr/bin/python

# Imports
import subprocess
import sys
import urllib.request
import urllib.error
import re
import os
import argparse
import time
import shutil
import http.client
from PIL import Image
from joblib import *
from xml.etree import ElementTree as ET


# Global Variables
IMAGES_TOTAL = 72
REGEX_MAIN_URL = r"(.+)/\?id=viewer&doc=(\w+)%2F(\w+)%2F\w+%2F\w+%2F\w+%2F(\w+).xml.*page_ref=(\d+).*"
REGEX = r"(http:\/\/.+\d\d\d\d_jpg_\/)(\d)_(\d+).jpg"
REGEX_FULL_PAGE = r"(http:\/\/.+)(\d\d\d\d).jpg(.+)"
REGEX_PATH = r".+(\d\d\d\d).jpg"
RATIO = {72: 8, 70: 10, 67: 9, 56: 7, 54: 8, 49: 7, 48: 8, 45: 7, 42: 7, 40: 8, 36: 6,
         35: 7, 30: 6, 28: 7, 27: 9, 25: 5, 24: 6, 20: 5, 18: 3, 16: 4, 15: 5, 12: 3, 8: 8, 1: 1}


# Functions
def download_image(url, img):
    try:
        urllib.request.urlretrieve(url, img)
    except:
        return False
    return True


def parse_main_url(url):
    if re.search(REGEX_MAIN_URL, url):
        match = re.search(REGEX_MAIN_URL, url)
        base_url = match.group(1)
        doc_1 = match.group(2)
        doc_2 = match.group(3)
        doc_3 = match.group(4)
        page_ref = match.group(5)
        return "http://" + base_url + "/" + doc_1 + "/" + doc_2 + "/datas/playlists/" + doc_3 + page_ref + ".xml"
    else:
        print('Can\'t match the url with the regex.')
        exit(1)


def process_main_url(url):
    with urllib.request.urlopen(parse_main_url(url)) as response:
        xml_content = response.read()
        return parse_xml(xml_content)


def modify_path(path):
    if re.search(REGEX_PATH, path):
        match = re.search(REGEX_PATH, path)
        page_number = int(match.group(1))
        if path.endswith('.jpg'):
            path = path[:-4] + '_jpg_/3_0.jpg'
            return (page_number, path)



def parse_xml(xml_content):
    xmldoc = ET.fromstring(xml_content)
    url = xmldoc.attrib['host'] + xmldoc.attrib['basepath']
    nb_pages = None
    unit_id = None
    date = None
    location = None
    path_pages_tuple_list = []
    for elem in xmldoc:
        if 't' == elem.tag:
            unit_id = elem.attrib['unitid']
            date = elem.text
        if 'g' == elem.tag:
            nb_pages = elem.attrib['nbi']
            for page in elem:
                if 't' == page.tag:
                    location = page.text
                if 'i' == page.tag:
                    for sub_elem in page:
                        if 'a' == sub_elem.tag:
                            path_pages_tuple_list.append(modify_path(sub_elem.text))
    name = unit_id + " - " + date + " - " + location
    path_pages_tuple_list.sort(key=lambda x: x[0])
    path_pages_list = [(index + 1, elem[1]) for index, elem in enumerate(path_pages_tuple_list)]
    return url, name, nb_pages, path_pages_list


def create_image(image_list, end_name, is_horizontal=True):
    images = list(map(Image.open, image_list))
    widths, heights = zip(*(i.size for i in images))

    total_width = sum(widths) if is_horizontal else max(widths)
    max_height = max(heights) if is_horizontal else sum(heights)

    new_im = Image.new('RGB', (total_width, max_height))

    x_offset = 0
    y_offset = 0
    for im in images:
        new_im.paste(im, (x_offset, y_offset))
        if is_horizontal:
            x_offset += im.size[0]
        else:
            y_offset += im.size[1]

    new_im.save(str(end_name) + '.jpg')


def append_images(start_image, end_image, end_name, is_horizontal):
    try:
        image_list = []
        for item in range(start_image, end_image):
            image_list.append(str(item) + ".jpg" if is_horizontal else "temp" + str(item) + ".jpg")
        create_image(image_list, end_name, is_horizontal)
    except Exception as e:
        print('Error: ' + str(e))


def check_url_exists(url):
    try:
        urllib.request.urlopen(url, timeout=10)
    except urllib.error.HTTPError as e:
        if e.getcode() == 304:
            return True
        return False
    except TimeoutError as e:
        return False
    return True


def initialize_zoom_variable(base_url):
    # Start matching
    if re.search(REGEX, base_url):
        match = re.search(REGEX, base_url)
        tempZoom = match.group(2)
        imageNumber = match.group(3)
        newUrl = match.group(1) + str(int(tempZoom) + 1) + "_" + str(int(imageNumber)) + ".jpg"
        if check_url_exists(newUrl) == True:
            zoom = int(tempZoom) + 1
            return zoom
        newUrl = match.group(1) + str(tempZoom) + "_" + str(int(imageNumber)) + ".jpg"
        if check_url_exists(newUrl) == True:
            zoom = int(tempZoom)
            return zoom
        newUrl = match.group(1) + str(int(tempZoom) - 1) + "_" + str(int(imageNumber)) + ".jpg"
        zoom = int(tempZoom) - 1
        return zoom


def find_right_url(base_url, current_image, zoom):
    # Start matching
    if re.search(REGEX, base_url):
        match = re.search(REGEX, base_url)
        newUrl = match.group(1) + str(zoom) + "_" + str(current_image) + ".jpg"
        return newUrl


def find_right_url_full_page(base_url, current_page):
    # Start matching
    if re.search(REGEX_FULL_PAGE, base_url):
        match = re.search(REGEX_FULL_PAGE, base_url)
        pageNumber = match.group(2)
        newUrl = match.group(1) + str(int(pageNumber) + current_page).zfill(4) + ".jpg" + match.group(3)
        return newUrl


def download_page(current_page, url):
    # Download
    os.makedirs("Page" + str(current_page), exist_ok=True)
    os.chdir("Page" + str(current_page))
    zoom = initialize_zoom_variable(url)
    for current_image in range(0, IMAGES_TOTAL):
        url = find_right_url(url, current_image, zoom)
        error = download_image(url, str(current_image + 1) + ".jpg")
        if error == False:
            break
    os.chdir("..")


def download_full_page(current_page, base_url, off_pages):
    # Download
    os.makedirs("Page" + str(current_page + off_pages + 1), exist_ok=True)
    os.chdir("Page" + str(current_page + off_pages + 1))
    url = find_right_url_full_page(base_url, current_page + off_pages)
    error = download_image(url, "1.jpg")
    os.chdir("..")


def convert_page(current_page, base_name, off_pages):
    # Convertion
    os.chdir("Page" + str(current_page + off_pages + 1))
    fileNumber = len(os.listdir(os.getcwd()))
    try:
        imagesPerRow = RATIO[fileNumber]
    except:
        print("Page " + str(current_page) +
              ": Ratio images per row / total images unknown, " + str(fileNumber))
        return
    column = int(fileNumber / imagesPerRow)
    fileNumber = imagesPerRow*column
    count = 1
    for c in range(1, fileNumber + 1, imagesPerRow):
        append_images(c, c + imagesPerRow, "temp" + str(count), True)
        count = count + 1
    append_images(1, column + 1, base_name + " - Page " +
                  str(current_page + off_pages + 1), False)
    shutil.move(base_name + " - Page " + str(current_page + off_pages + 1) + ".jpg",
                "../" + base_name + " - Page " + str(current_page + off_pages + 1) + ".jpg")
    os.chdir("..")
    shutil.rmtree("Page" + str(current_page + off_pages + 1))


def main(argv):
    # Start main
    parser = argparse.ArgumentParser(
        description='Mnesys2 download helper script written in Python3. Requires joblib (pip install joblib)')
    parser.add_argument('-u', '--url', dest="url",
                        help='url of the first image')
    parser.add_argument('-n', '--name', dest="name",
                        default="Archive", help='name for both folder and pages')
    parser.add_argument('-p', '--pages', type=int, dest="pages",
                        default=1, help='total number of pages')
    parser.add_argument('-o', '--off-pages', type=int,
                        dest="off_pages", default=0, help='set an off-pages number')
    parser.add_argument('-f', '--full-page', type=bool, dest="fullpage",
                        default=False, help="one image per page, default False")
    args = parser.parse_args()
    # Set the global variables
    base_url = args.url
    base_name = args.name
    pages_total = args.pages
    off_pages = args.off_pages
    fullpage = args.fullpage
    # Starting download
    print("Download started.\r")
    if fullpage == False:
        base_url, base_name, pages_total, path_pages_list = process_main_url(base_url)
        os.makedirs(base_name, exist_ok=True)
        os.chdir(base_name)
        Parallel(n_jobs=int(20))(delayed(download_page)(page_tuple[0], base_url + page_tuple[1]) for page_tuple in path_pages_list)
    else:
        os.makedirs(base_name, exist_ok=True)
        os.chdir(base_name)
        for j in range(pages_total):
            download_full_page(j, base_url, off_pages)
    print("Download finished.\r")
    sys.stdout.flush()
    # Starting converting
    print("Convert started.\r")
    Parallel(n_jobs=int(20))(delayed(convert_page)(
        j, base_name, off_pages) for j in range(int(pages_total)))
    print("Convert finished.\r")


if __name__ == "__main__":
    main(sys.argv)
