from selenium import webdriver

import urllib.request as urllibreq
import json
import time
import os
import ctypes
import datetime
import requests

# adding path to geckodriver to the OS environment variable
os.environ["PATH"] += os.pathsep + os.getcwd()
DRIVE = u'e:'
# ROOT = DRIVE + os.sep + "Dataset"
ROOT = "Dataset"
THIS_YEAR = datetime.datetime.now().year
SEARCH_YEAR_PERIOD = 15
DOWNLOAD_LIMIT = 100
TIME_OUT = 15
VIEWS = ['Front', 'Right', 'Left', 'Rear']
SCROLL_COUNT = 4


def main():
	if not os.path.exists(ROOT):
		os.makedirs(ROOT)

	total_downloaded_count = 0
	header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0'}
	extensions = {"jpg", "jpeg", "png", "gif"}

	f = open('BestCars.txt')
	line = f.readline()

	while line:
		search_model = str(line).replace('\r', '').replace('\n', '').split(',')
		make = search_model[0]
		model = search_model[1]
		start_year = int(search_model[2])
		end_year = int(search_model[3])

		if end_year == 0:
			end_year = THIS_YEAR

		year = end_year
		make_path = ROOT + os.sep + make.replace(' ', '_')

		if not os.path.exists(make_path):
			os.makedirs(make_path)
		makemodel_path = make_path + os.sep + model.replace(' ', '_')

		if not os.path.exists(makemodel_path):
			os.makedirs(makemodel_path)

		for i in range(0, SEARCH_YEAR_PERIOD, 1):
			makemodelyear_path = makemodel_path + os.sep + str(year)
			if not os.path.exists(makemodelyear_path):
				os.makedirs(makemodelyear_path)

			#driver = None
			for j in range(0, len(VIEWS), 1):
				sub_trying_count = 0
				sub_downloaded_count = 0
				save_path = makemodelyear_path + os.sep + VIEWS[j]
				if not os.path.exists(save_path):
					os.makedirs(save_path)
				searchtext = ' '.join([make, model, str(year), VIEWS[j]]).replace(' ', '%20')
				print('Search Text:', searchtext.replace('%20', ' '))
				url = "https://www.google.co.in/search?q=" + searchtext + "&source=lnms&tbm=isch"
				# if driver is not None:
				# 	driver.quit()

				driver = webdriver.Firefox()
				driver.get(url)
				driver.minimize_window()

				if False:
					for _ in range(int(SCROLL_COUNT)):
						for __ in range(10):
							# multiple scrolls needed to show all 400 images
							driver.execute_script("window.scrollBy(0, 1000000)")
							time.sleep(0.2)
						# to load next 400 images
						time.sleep(0.5)
						try:
							driver.find_element_by_xpath("//input[@value='Show more results']").click()
						except Exception as e:
							# print("Less images found:", e)
							break

				images = driver.find_elements_by_xpath('//div[contains(@class,"rg_meta")]')
				# print("Total searched images:", len(images))
				for img in images:
					sub_trying_count += 1
					success = False

					# print("\nDownloading image", sub_trying_count)
					try:
						img_url = json.loads(img.get_attribute('innerHTML'))["ou"]
						img_type = json.loads(img.get_attribute('innerHTML'))["ity"]
						# print(img_url)

					except Exception as e:
						pass
						# print('    xXx -> Failed: json query failed:', e)
					else:
						try:
							if img_type not in extensions:
								img_type = 'jpg'

							file_name = '_'.join([make, model, str(year), VIEWS[j], str(sub_downloaded_count)]) + '.' + img_type
							image_fullpath = os.path.join(save_path, file_name)

							content = requests.get(img_url, timeout=TIME_OUT).content
							if content is not None:
								file = open(image_fullpath, 'wb')
								file.write(content)
								file.close()
						except Exception as e:
							# print('    xxxXXXXXxxx(1) -> Failed'.format(img_url), e)
							try:
								urllibreq.urlretrieve(img_url, image_fullpath, timeout=TIME_OUT)
							except Exception as e:
								pass
								# print('    xxxXXXXXxxx(2) -> Failed'.format(img_url), e)
							else:
								success = True

						else:
							success = True

						finally:
							if os.path.isfile(image_fullpath) and os.path.getsize(image_fullpath) > 0:
								if success:
									# print('  oooOOOOOooo-> Success')
									sub_downloaded_count += 1
							else:
								pass
								# print('  xxxXXXXXxxx -> Failed: File is Empty!')

					if sub_downloaded_count >= DOWNLOAD_LIMIT:
						break;

				# print("Sub. Total Downloaded: ", sub_downloaded_count, "/", sub_trying_count, "\n")
				total_downloaded_count += sub_downloaded_count
				driver.quit()

			if start_year >= year:
				break;
			else:
				year -= 1

		line = f.readline()
		free_bytes = ctypes.c_ulonglong(0)
		ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p(DRIVE), None, None, ctypes.pointer(free_bytes))
		freespace = free_bytes.value / 1024 / 1024
		# print(make, model, 'finish!')
		# print('Free Space:', int(freespace / 1024), 'GB\n')
		if freespace < 1024:
			break;

	f.close()
	# print("\nFinish Downloading! Total Downloaded: ", total_downloaded_count)

if __name__ == "__main__":
	main()