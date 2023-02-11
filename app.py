import os
import requests
import time
from selenium import webdriver
from selenium.webdriver.common.by import By

driverPath = "./chromedriver"
searchString = "car"
numbersOfImage = 10
targetPath = "./images"


def scrollToEnd(wd, sleepTime):
    wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(sleepTime)


def fetchImagesUrls(searchString, numberOfImages, wd, sleepBetweenInteractions: int = 1):
    searchUrl = "https://www.google.com/search?q={query}&rlz=1C5CHFA_enIN1027IN1027&sxsrf=AJOqlzXXKQ8PUdiYy2Nx2ZwtXrrDRoxIOw:1676117767422&source=lnms&tbm=isch&sa=X&ved=2ahUKEwjctYOhuY39AhWkTWwGHTw_AGwQ_AUoA3oECAEQBQ&biw=1280&bih=689&dpr=1"
    wd.get(searchUrl.format(query=searchString))
    imageUrls = set()
    imageCount = resultsStart = 0
    while len(imageUrls) < numberOfImages:
        scrollToEnd(wd, sleepBetweenInteractions)
        # thumbnailResults = wd.find_elements("css_selector", "img.Q4LuWd")
        thumbnailResults = wd.find_elements(By.CLASS_NAME, "Q4LuWd")
        numberOfResults = len(thumbnailResults)
        for img in thumbnailResults[:numberOfResults + 1]:
            try:
                img.click()
                time.sleep(sleepBetweenInteractions)
            except Exception:
                continue
            actualImages = wd.find_elements(By.CLASS_NAME, "n3VNCb")
            for actualImage in actualImages:
                try:
                    url = actualImage.get_attribute("src")
                    if url and "http" in url:
                        imageUrls.add(url)
                except Exception as error:
                    continue
            imageCount = len(imageUrls)
            if imageCount >= numberOfImages:
                print(f"Found: {imageCount} image links, done!")
                break
        else:
            print(f"Found {imageCount} image links, looking foe more...")
            time.sleep(30)
            return
            # loadMoreImages = wd.find_elements_by_css_selector(".mye4qd")
            # if loadMoreImages:
            #     wd.execute_script("document.querySelector('.mye4qd').click();")
        resultsStart = len(thumbnailResults)
    return imageUrls


def persist_image(targetFolder, url, counter):
    global imageContent
    try:
        imageContent = requests.get(url).content
    except Exception as error:
        print(f"Could not Download {url} -> {error}")
    try:
        file = open(os.path.join(targetFolder, "jpg_" + str(counter) + ".jpg"), "wb")
        file.write(imageContent)
        print("SUCCESSFULLY IMAGE IS SAVED")
    except Exception as error:
        print(f"Could not save images {url} -> {error}")


def searchAndDownload(driverPath, searchString, targetPath, numbersOfImage=10):
    targetFolder = os.path.join(targetPath, "_".join(searchString.lower().split()))
    # print(os.path.join("/image"))
    if not os.path.exists(targetFolder):
        os.makedirs(targetFolder)
    with webdriver.Chrome() as wd:
        result = fetchImagesUrls(searchString, numbersOfImage, wd, 0.5)
    counter = 0
    for url in result:
        persist_image(targetFolder, url, counter)
        counter += 1


searchAndDownload(driverPath, searchString, targetPath, numbersOfImage)
