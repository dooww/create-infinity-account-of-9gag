#import packages

from selenium import webdriver
from selenium.webdriver import Firefox
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup, NavigableString, Tag
import pandas as pd
import os,sys
import time
import random
import warnings
import requests
from bs4 import BeautifulSoup
import imaplib,email
from email.parser import HeaderParser
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
import csv
import requests


#firefox_options
option = webdriver.FirefoxOptions()
option.add_argument('lang=en')
option.add_argument("--mute-audio")
#option.add_experimental_option("excludeSwitches", ["enable-logging"])
# option.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
option.add_argument("user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 10_3 like Mac OS X) AppleWebKit/602.1.50 (KHTML, like Gecko) CriOS/56.0.2924.75 Mobile/14E5239e Safari/602.1")

#audio to text
def audioToText(mp3Path):
    audioToTextDelay = 10
    googleIBMLink = 'https://speech-to-text-demo.ng.bluemix.net/'

    driver.execute_script('''window.open("","_blank");''')
    driver.switch_to.window(driver.window_handles[1])

    driver.get(googleIBMLink)

    # Upload file

    time.sleep(1)
    driver.execute_script("window.scrollTo(0, 1000);")
    root = driver.find_element_by_id('root').find_elements_by_class_name('dropzone _container _container_large')
    btn = driver.find_element(By.XPATH, '//*[@id="root"]/div/input')
    btn.send_keys(mp3Path)

    # Audio to text is processing

    time.sleep(audioToTextDelay)

    driver.execute_script("window.scrollTo(0, 1000);")
    text = driver.find_elements(By.XPATH, '//*[@id="root"]/div/div[6]/div/div/div/span')
    result = " ".join( [ each.text for each in text ] )

    driver.close()
    driver.switch_to.window(driver.window_handles[0])

    return result

def saveFile(content,filename):
    with open(filename, "wb") as handle:
        for data in content.iter_content():
            handle.write(data)

def CAPTCHA():
    print(driver.find_element_by_tag_name('body').text)
    googleClass = driver.find_element_by_css_selector('.field.captcha')
    outeriframe = googleClass.find_element_by_tag_name('iframe')
    outeriframe.click()

    print("\n[>] Try Bypass reCAPTCHA...")

    allIframesLen = driver.find_elements_by_tag_name('iframe')
    audioBtnFound = False
    audioBtnIndex = -1

    for index in range(len(allIframesLen)):
        driver.switch_to.default_content()
        iframe = driver.find_elements_by_tag_name('iframe')[index]
        driver.switch_to.frame(iframe)
        driver.implicitly_wait(2)
        try:
            audioBtn = driver.find_element_by_id('recaptcha-audio-button') or driver.find_element_by_id('recaptcha-anchor')
            audioBtn.click()
            audioBtnFound = True
            audioBtnIndex = index
            break
        except Exception as e:
            pass

    if audioBtnFound:
        try:
            while True:
                href = driver.find_element_by_id('audio-source').get_attribute('src')
                print('***************************************************')
                print(href)
                response = requests.get(href, stream=True)
                saveFile(response,filename)
                delay()
                response = audioToText(os.getcwd() + '/' + filename)

                driver.switch_to_default_content()
                iframe = driver.find_elements_by_tag_name('iframe')[audioBtnIndex]
                driver.switch_to.frame(iframe)

                inputbtn = driver.find_element_by_id('audio-response')
                inputbtn.send_keys(response)
                inputbtn.send_keys(Keys.ENTER)

                time.sleep(2)
                errorMsg = driver.find_elements_by_class_name('rc-audiochallenge-error-message')[0]

                if errorMsg.text == "" or errorMsg.value_of_css_property('display') == 'none':
                    print("\n[>] Success")
                    break

        except Exception as e:
            print(e)
            print('\n[>] Caught. Try to change proxy now.')
    else:
        print('\n[>] Button not found. This should not happen.')

#wait function

def delay ():
    time.sleep(random.randint(2,3))
##############################################################################################################################
def create(mail,pass):

    link1=driver.find_element_by_css_selector(".alternative a")
    print("hhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh")
    # driver.findElement(By.linkText("Sign up with your"))
    print(link1.text)
    link1.click()

    delay()
    delay()
    delay()
    name_el=driver.find_elements_by_id('signup-email-name')[0]
    email_el=driver.find_elements_by_id('signup-email-email')[0]
    pass_el=driver.find_elements_by_id('signup-email-password')[0]
    # print(len(name_el),len(email_el),len(pass_el))
    name_el.send_keys('dow')
    email_el.send_keys('email@ff.com')
    pass_el.send_keys('passss')
    #     pass_the_capture()
    delay()
    driver.find_element_by_css_selector('.btn.left').click()
    age_el=driver.find_element_by_id('signup-email-age')
    age_el.send_keys('20')
    delay()
    CAPTCHA()
    driver.find_element_by_css_selector('.btn.left').click()
    confirmation_code=getconfirmation(mail,pass)
    confirm=driver.find_elements_by_tag_name('input')[0]
    name_el.send_keys(confirmation_code)
    driver.find_element_by_css_selector('.btn.left').click()
#####################################################################################################################
def get_inbox(username,password,host):
    mail = imaplib.IMAP4_SSL(host)
    mail.login(username, password)
    mail.select("inbox")
    _, search_data = mail.search(None, 'UNSEEN')
    my_message = []
    for num in search_data[0].split():
        email_data = {}
        _, data = mail.fetch(num, '(RFC822)')
        # print(data[0])
        _, b = data[0]
        email_message = email.message_from_bytes(b)
        for header in ['subject', 'to', 'from', 'date']:
            print("{}: {}".format(header, email_message[header]))
            email_data[header] = email_message[header]
        for part in email_message.walk():
            if part.get_content_type() == "text/plain":
                body = part.get_payload(decode=True)
                email_data['body'] = body.decode()
            elif part.get_content_type() == "text/html":
                html_body = part.get_payload(decode=True)
                email_data['html_body'] = html_body.decode()
        my_message.append(email_data)
    return my_message

# confirm_email()
def getconfirmation(mail,pass):
    # Connect to imap server
    username = mail
    password = pass
    host = get_host(mail)
    inbox=get_inbox(username,password,host)
    return int(inbox[0].body)

#open driver and browser
# path="./geckodriver"
#driver=webdriver.Firefox(path)
file = open('checker.txt', 'r')
emails = file1.readlines()
file1 = open('proxies.txt', 'r')
proxies = file1.readlines()

for x in range len(emails) :
    try :
        driver = webdriver.Firefox(firefox_options=option,proxy=proxies[x])
        driver.get('https://9gag.com/signup')
        delay()
        create(emails[x].split(':')[0],emails[x].split(':')[1])
        driver.close()
    except :
        print('An exception occurred mail  can be used already')
