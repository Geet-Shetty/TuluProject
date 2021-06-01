from selenium import webdriver
from time import sleep
opera_profile = r'C:/Users/Geet Shetty/AppData\Roaming/Opera Software/Opera Stable'
options = webdriver.ChromeOptions()
options.add_argument('user-data-dir=' + opera_profile)
options._binary_location = r'C:/Users/Geet Shetty/AppData/Local/Programs/Opera/76.0.4017.94/opera.exe'
driver = webdriver.Opera(executable_path=r'D:/programs/webstuff/operadriver.exe',options=options)
driver.get('https://whatismyipaddress.com')
# sleep(10)
# driver.quit()