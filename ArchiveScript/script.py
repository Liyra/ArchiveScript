#!/usr/bin/python

# Imports
import subprocess, sys, urllib.request, urllib.error, re, os, argparse, time, shutil, http.client
from joblib import *

# Global Variables
imagesTotal = 54
regex = r"(http:\/\/.+)_(\d\d\d\d)_jpg_\/(\d)_(\d).jpg"
ratio = {54: 9, 49: 7, 48: 8, 45: 7, 42: 7, 40: 8, 36:6, 35: 7, 30: 6, 28: 7, 24: 6, 25: 5, 16: 4, 12:3}

# Functions
def DownloadImage(url, img):
	try:
		urllib.request.urlretrieve(url, img)
	except:
		return False
	return True

def AppendImgs(startImg, endImg, endName, width):
	fromFiles = ""
	if width == True:
		for item in range(startImg, endImg):
			fromFiles = fromFiles + str(item) + ".jpg "
		subprocess.run("convert " + fromFiles + "+append " + endName + ".jpg", shell=True, check=True)
	else:
		for item in range(startImg, endImg):
			fromFiles = fromFiles + "temp" + str(item) + ".jpg "
		subprocess.run("convert " + fromFiles + "-append " + endName + ".jpg", shell=True, check=True)

def CheckUrlExists(url):
	try:
		urllib.request.urlopen(url)
	except urllib.error.HTTPError as e:
		if e.getcode() == 304:
			return True
		return False
	return True

def InitializeZoomVariable(currentPage, baseURL, regex):
	# Start matching
	if re.search(regex, baseURL):
		match = re.search(regex, baseURL)
		pageNumber = match.group(2)
		tempZoom = match.group(3)
		imageNumber = match.group(4)
		newUrl = match.group(1) + "_" + str(int(pageNumber) + currentPage).zfill(4) + "_jpg_/" + str(int(tempZoom) + 1) + "_" + str(int(imageNumber)) + ".jpg"
		if CheckUrlExists(newUrl) == True:
			zoom = int(tempZoom) + 1
			return zoom
		newUrl = match.group(1) + "_" + str(int(pageNumber) + currentPage).zfill(4) + "_jpg_/" + str(tempZoom) + "_" + str(int(imageNumber)) + ".jpg"
		if CheckUrlExists(newUrl) == True:
			zoom = int(tempZoom)
			return zoom
		newUrl = match.group(1) + "_" + str(int(pageNumber) + currentPage).zfill(4) + "_jpg_/" + str(int(tempZoom) - 1) + "_" + str(int(imageNumber)) + ".jpg"
		zoom = int(tempZoom) - 1
		return zoom

def FindRightUrl(baseURL, currentPage, currentImage, zoom, regex):
	# Start matching
	if re.search(regex, baseURL):
		match = re.search(regex, baseURL)
		pageNumber = match.group(2)
		imageNumber = match.group(4)
		newUrl = match.group(1) + "_" + str(int(pageNumber) + currentPage).zfill(4) + "_jpg_/" + str(zoom) + "_" + str(int(imageNumber) + currentImage) + ".jpg"
		return newUrl

def DownloadPage(currentPage, imagesTotal, baseURL, offPages, regex):
		# Download
		os.makedirs("Page" + str(currentPage + offPages + 1), exist_ok=True)
		os.chdir("Page" + str(currentPage + offPages + 1))
		zoom = InitializeZoomVariable(currentPage + offPages, baseURL, regex)
		for currentImage in range (0, imagesTotal):
			url = FindRightUrl(baseURL, currentPage + offPages, currentImage, zoom, regex)
			error = DownloadImage(url, str(currentImage + 1) + ".jpg")
			if error == False:
			  break
		os.chdir("..")

def ConvertPage(currentPage, baseName, pagesTotal, ratio, offPages):
	# Convertion
  os.chdir("Page" + str(currentPage + offPages + 1))
  fileNumber = len(os.listdir(os.getcwd()))
  try:
    imagesPerRow = ratio[fileNumber]
  except:
    print("Page " + currentPage + ": Ratio images per row / total images unknown, " + str(fileNumber))
    return
  column = int(fileNumber / imagesPerRow)
  fileNumber = imagesPerRow*column
  count = 1
  for c in range(1, fileNumber + 1, imagesPerRow):
    AppendImgs(c, c + imagesPerRow, "temp" + str(count), True)
    count = count + 1
  AppendImgs(1, column + 1, "\"" + baseName + " - Page " + str(currentPage + offPages + 1) + "\"", False)
  shutil.move(baseName + " - Page " + str(currentPage + offPages + 1) + ".jpg", "../" + baseName + " - Page " + str(currentPage + offPages + 1) + ".jpg")
  os.chdir("..")
  shutil.rmtree("Page" + str(currentPage + offPages + 1))

def main():
	# Global declaration
	global imagesTotal
	global ratio
	global regex
	# Start main
	parser = argparse.ArgumentParser(description='Mnesys2 download helper script written in Python3. Requires joblib (pip install joblib)')
	parser.add_argument('-u', '--url', dest="url",help='url of the first image')
	parser.add_argument('-n', '--name', dest="name", default="Archive", help='name for both folder and pages')
	parser.add_argument('-p', '--pages', type=int, dest="pages", default=1, help='total number of pages')
	parser.add_argument('-o', '--off-pages', type=int, dest="offPages", default=0, help='set an off-pages number')
	args = parser.parse_args()
	# Set the global variables
	baseURL=args.url
	baseName=args.name
	pagesTotal=args.pages
	offPages=args.offPages
	# Starting download
	os.makedirs(baseName, exist_ok=True)
	os.chdir(baseName)
	print ("Download started.\r")
	Parallel(n_jobs=int(20))(delayed(DownloadPage)(j, imagesTotal, baseURL, offPages, regex) for j in range(pagesTotal))
	print ("Download finished.\r")
	sys.stdout.flush()
	# Starting converting
	print("Convert started.\r")
	Parallel(n_jobs=int(20))(delayed(ConvertPage)(j, baseName, pagesTotal, ratio, offPages) for j in range(pagesTotal))
	print("Convert finished.\r")

if __name__ == "__main__":
    main()
