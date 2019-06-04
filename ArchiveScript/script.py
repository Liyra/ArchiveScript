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
from joblib import *


# Global Variables
imagesTotal = 72
regex = r"(http:\/\/.+)(\d\d\d\d\d)_jpg_\/(\d)_(\d).jpg"
regexFullPage = r"(http:\/\/.+)(\d\d\d\d).jpg(.+)"
ratio = {72: 8, 70: 10, 67: 9, 56: 7, 54: 8, 49: 7, 48: 6, 45: 7, 42: 7, 40: 8, 36: 6,
         35: 7, 30: 6, 28: 7, 27: 9, 25: 5, 24: 6, 20: 4, 18: 3, 16: 4, 15: 3, 12: 3, 8: 8, 1: 1}


# Functions
def DownloadImage(url, img):
    try:
        urllib.request.urlretrieve(url, img)
    except:
        return False
    return True


def AppendImgs(startImg, endImg, endName, width):
    try:
        fromFiles = ""
        if width == True:
            for item in range(startImg, endImg):
                fromFiles = fromFiles + str(item) + ".jpg "
            subprocess.run("\"../../ImageMagick/convert\" " + fromFiles +
                           "+append " + endName + ".jpg", shell=True, check=True)
        else:
            for item in range(startImg, endImg):
                fromFiles = fromFiles + "temp" + str(item) + ".jpg "
            subprocess.run("\"../../ImageMagick/convert\" " + fromFiles +
                           "-append " + endName + ".jpg", shell=True, check=True)
    except Exception as e:
        print('Error: ' + str(e))


def CheckUrlExists(url):
    try:
        urllib.request.urlopen(url, timeout=10)
    except urllib.error.HTTPError as e:
        if e.getcode() == 304:
            return True
        return False
    except TimeoutError as e:
        return False
    return True


def InitializeZoomVariable(currentPage, baseURL, regex):
    # Start matching
    if re.search(regex, baseURL):
        match = re.search(regex, baseURL)
        pageNumber = match.group(2)
        tempZoom = match.group(3)
        imageNumber = match.group(4)
        newUrl = match.group(1) + "_" + str(int(pageNumber) + currentPage).zfill(
            4) + "_jpg_/" + str(int(tempZoom) + 1) + "_" + str(int(imageNumber)) + ".jpg"
        if CheckUrlExists(newUrl) == True:
            zoom = int(tempZoom) + 1
            return zoom
        newUrl = match.group(1) + "_" + str(int(pageNumber) + currentPage).zfill(
            4) + "_jpg_/" + str(tempZoom) + "_" + str(int(imageNumber)) + ".jpg"
        if CheckUrlExists(newUrl) == True:
            zoom = int(tempZoom)
            return zoom
        newUrl = match.group(1) + "_" + str(int(pageNumber) + currentPage).zfill(
            4) + "_jpg_/" + str(int(tempZoom) - 1) + "_" + str(int(imageNumber)) + ".jpg"
        zoom = int(tempZoom) - 1
        return zoom


def FindRightUrl(baseURL, currentPage, currentImage, zoom, regex):
    # Start matching
    if re.search(regex, baseURL):
        match = re.search(regex, baseURL)
        pageNumber = match.group(2)
        imageNumber = match.group(4)
        newUrl = match.group(1) + "_" + str(int(pageNumber) + currentPage).zfill(
            4) + "_jpg_/" + str(zoom) + "_" + str(int(imageNumber) + currentImage) + ".jpg"
        return newUrl


def FindRightUrlFullPage(baseURL, currentPage, regex):
    # Start matching
    if re.search(regex, baseURL):
        match = re.search(regex, baseURL)
        pageNumber = match.group(2)
        newUrl = match.group(1) + str(int(pageNumber) +
                                      currentPage).zfill(4) + ".jpg" + match.group(3)
        return newUrl


def DownloadPage(currentPage, imagesTotal, baseURL, offPages, regex):
        # Download
    os.makedirs("Page" + str(currentPage + offPages + 1), exist_ok=True)
    os.chdir("Page" + str(currentPage + offPages + 1))
    zoom = InitializeZoomVariable(currentPage + offPages, baseURL, regex)
    for currentImage in range(0, imagesTotal):
        url = FindRightUrl(baseURL, currentPage + offPages,
                           currentImage, zoom, regex)
        error = DownloadImage(url, str(currentImage + 1) + ".jpg")
        if error == False:
            break
    os.chdir("..")


def DownloadFullPage(currentPage, baseURL, offPages, regex):
    # Download
    os.makedirs("Page" + str(currentPage + offPages + 1), exist_ok=True)
    os.chdir("Page" + str(currentPage + offPages + 1))
    url = FindRightUrlFullPage(baseURL, currentPage + offPages, regex)
    error = DownloadImage(url, "1.jpg")
    os.chdir("..")


def ConvertPage(currentPage, baseName, pagesTotal, ratio, offPages):
    # Convertion
    os.chdir("Page" + str(currentPage + offPages + 1))
    fileNumber = len(os.listdir(os.getcwd()))
    try:
        imagesPerRow = ratio[fileNumber]
    except:
        print("Page " + str(currentPage) +
              ": Ratio images per row / total images unknown, " + str(fileNumber))
        return
    column = int(fileNumber / imagesPerRow)
    fileNumber = imagesPerRow*column
    count = 1
    for c in range(1, fileNumber + 1, imagesPerRow):
        AppendImgs(c, c + imagesPerRow, "temp" + str(count), True)
        count = count + 1
    AppendImgs(1, column + 1, "\"" + baseName + " - Page " +
               str(currentPage + offPages + 1) + "\"", False)
    shutil.move(baseName + " - Page " + str(currentPage + offPages + 1) + ".jpg",
                "../" + baseName + " - Page " + str(currentPage + offPages + 1) + ".jpg")
    os.chdir("..")
    shutil.rmtree("Page" + str(currentPage + offPages + 1))


def main(argv):
    # Global declaration
    global imagesTotal
    global ratio
    global regex
    global regexFullPage
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
                        dest="offPages", default=0, help='set an off-pages number')
    parser.add_argument('-f', '--full-page', type=bool, dest="fullpage",
                        default=False, help="one image per page, default False")
    args = parser.parse_args()
    # Set the global variables
    baseURL = args.url
    baseName = args.name
    pagesTotal = args.pages
    offPages = args.offPages
    fullpage = args.fullpage
    # Starting download
    os.makedirs(baseName, exist_ok=True)
    os.chdir(baseName)
    print("Download started.\r")
    if fullpage == False:
        Parallel(n_jobs=int(20))(delayed(DownloadPage)(j, imagesTotal,
                                                       baseURL, offPages, regex) for j in range(pagesTotal))
    else:
        for j in range(pagesTotal):
            DownloadFullPage(j, baseURL, offPages, regexFullPage)
    print("Download finished.\r")
    sys.stdout.flush()
    # Starting converting
    print("Convert started.\r")
    Parallel(n_jobs=int(20))(delayed(ConvertPage)(
        j, baseName, pagesTotal, ratio, offPages) for j in range(pagesTotal))
    print("Convert finished.\r")


if __name__ == "__main__":
    main(sys.argv)
