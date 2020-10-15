from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from Project.functions import validate_url, login


# Driver settings
options = Options()
options.add_argument('--window-size=1920,1080')
options.add_argument('--start-maximized')
options.add_argument('--headless')
options.add_experimental_option(
    'prefs', {
        'download.prompt_for_download': False,
        'download.directory_upgrade': True,
        'safebrowsing_for_trusted_sources_enabled': True,
        'safebrowsing.enabled': True
    }
)
driver = webdriver.Chrome(chrome_options=options)


def main(web_driver_object):
    """
    :param web_driver_object: Type enforcement of object?
    :return:
    """
    print('\n\nPython 3.8 | Apache Selenium | Kaseya VSA')
    print('Starting column_sets application - MSP Builder, LLC')
    print('\n\nEnsure that you have User, PW, and MFA prepared.')
    print('note: This application can be terminated at any time with CTRL+C, CTRL+C break sequence.')
    print('note: You cannot ctrl+v passwords through console masked input.\n')
    print('URL entry format: subdomain.sld.tld')
    url = input('Provide VSA Url: ')
    url = validate_url(url)
    url = 'https://' + url
    print('Launching headless Chrome connection to ' + url + '\n')
    web_driver_object.get(url)
    driver.implicitly_wait(3)
    login(driver)
