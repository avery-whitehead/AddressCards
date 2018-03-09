import json
from time import sleep
from selenium import webdriver
from selenium.webdriver.support.ui import Select


# 150 DPI A5 size, accounting for window borders
options = webdriver.ChromeOptions()
options.add_argument('window-size=1139,826')

driver = webdriver.Chrome(executable_path='./chromedriver.exe', chrome_options=options)

def print_page(driver, pages):
    for page in pages:
        path = 'file:///C:/Users/jwhitehead/Documents/Python/Address%20Postcards/out/{}.html'.format(page)
        driver.get(path)
        sleep(1)
        driver.save_screenshot('{}.png'.format(page))

if __name__ == '__main__':
    pages = ['010001279831-addr', '010001279831-cal']
    print_page(driver, pages)
