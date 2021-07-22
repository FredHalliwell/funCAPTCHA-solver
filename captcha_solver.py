from typing import final
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

#for screenshotting
from PIL import Image

from time import sleep

import io
import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"]=r'sturdy-carver-284009-c11971bd8613.json'



# Imports the Google Cloud client library
from google.cloud import vision



#load captcha site
#take cropped screenshot
def load_site():

    #define driver as chrome, load webpage
    global driver
    driver = webdriver.Chrome()
    driver.get("https://2captcha.com/demo/rotatecaptcha")

    sleep(5)


def get_img():

    #get animal element
    animal_image = driver.find_element_by_xpath("/html/body/div[1]/div[2]/div/div/div/div[1]/div/div/div/div/div/div[2]/div/form/div/div[2]/div/img")


    #gets XY coords of image, gets size of image
    location = animal_image.location
    size = animal_image.size

    #save screenshot
    driver.save_screenshot("fullPageScreenshot.png")
    x = location['x']
    y = location['y']
    w = x + size['width']
    h = y + size['height']

    fullImg = Image.open("fullPageScreenshot.png")
    cropImg = fullImg.crop((x, y, w, h))
    cropImg.save('cropImage.png')



def test_img():

    global current_confidence
    current_confidence = 0


   # print("current conf = ", current_confidence)

    #current_confidence = 0
    
    # Instantiates a client
    client = vision.ImageAnnotatorClient()

    # The name of the image file to annotate
    file_name = os.path.abspath('cropImage.png')

    # Loads the image into memory
    with io.open(file_name, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    # Performs label detection on the image file
    response = client.label_detection(image=image)
    labels = response.label_annotations

    #print("")
    #print('Labels:')
    for label in labels:

        #print(label.description, label.score)
        if "animal" in label.description:

            current_confidence = label.score

            


#check position for each rotation click
def rotate_img():

    #variable which saves the highest confidence 
    highest_confidence = 0
    
    #saves the number of rotations the animal has made
    rotations = 0

    #definse the Left arrow
    global arrowL
    arrowL = driver.find_element_by_xpath("/html/body/div[1]/div[2]/div/div/div/div[1]/div/div/div/div/div/div[2]/div/form/div/div[1]")

    #rotations needed to turn 360*
    for i in range(24):

        #add 1 to rotations amount
        rotations +=1
        #take a screenshot
        get_img()
        #test the screenshot for confidence
        test_img()
        #rotate once
        arrowL.click()

        #save the highest confidence level, and the amount of rotations needed to reach it
        if current_confidence > highest_confidence:
            highest_confidence = current_confidence

            print("highest confidence = ", highest_confidence)
            rotations_amount = rotations

    #click the arrow enough times to rotate it back to most confident position
    for i in range(rotations_amount):
        arrowL.click()
    
    sleep(1)
    submit_button = driver.find_element_by_xpath("/html/body/div[1]/div[2]/div/div/div/div[1]/div/div/div/div/div/div[2]/div/form/button")
    submit_button.click()

    


load_site()
get_img()
test_img()

rotate_img()

