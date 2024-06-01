from selenium import webdriver
from selenium.common import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import time

from selenium.webdriver.chrome.service import Service
### Prosze sprawdzic readme.md zeby zobaczyc zdjecia
# ### Niestety strona zmienila swoj layout kilka dni przed oddaniem projektu, przez co skrypt do pobierania danych nie dziala poprawnie.
# Tak wygladal stary layout strony:
# ![img.png](img.png)
#
#
# Tak wyglada nowy:
# ![img_1.png](img_1.png)
# Zniknelo wiec sporo informacji o technologiach w ofercie pracy, lokalizacji, oraz zmienily sie nazwy pól, divów, etc.
# Trzeba bt zmodyfikowac skrypt, jednak stracilbym sporo przydatnych informacji, wiec zdecydowalem sie zostawic stary skrypt.

class JobOffer:
    def __init__(self, offer_name=None, salaries=None, company=None, work_modes=None, office=None, whole_poland=None,
                 technologies=None, seniority=None):
        self.offer_name = offer_name
        self.salaries = salaries
        self.company = company
        self.work_modes = work_modes
        self.office = office
        self.whole_poland = whole_poland
        self.technologies = technologies
        self.seniority = seniority

    def __str__(self):
        return f'Offer name: {self.offer_name}, Salaries: {self.salaries}, Company: {self.company}, Type of work: {self.work_modes}, Office: {self.office}, Whole Poland: {self.whole_poland}, Technologies: {self.technologies}, Seniority: {self.seniority}'

    def write_to_csv(self):
        with open('job_offers.csv', 'a') as file:
            file.write(
                f'{self.offer_name}, {self.salaries}, {self.company}, {self.work_modes}, {self.office}, {self.whole_poland}, {self.technologies}, {self.seniority}\n')

    def to_dict(self):
        return {
            'offer_name': self.offer_name,
            'salaries': self.salaries,
            'company': self.company,
            'work_modes': self.work_modes,
            'office': self.office,
            'whole_poland': self.whole_poland,
            'technologies': self.technologies,
            'seniority': self.seniority
        }

    def __repr__(self):
        return self.__str__()


service_instance = Service()
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument("--headless=new")
driver = webdriver.Chrome(options=chrome_options)
# driver = webdriver.Chrome(service=service_instance)

driver.get('https://theprotocol.it/filtry/1;s')
driver.maximize_window()

accept_button = driver.find_element(By.CSS_SELECTOR, 'button[data-test="button-acceptAll"]')
accept_button.click()

pages = driver.find_elements(By.CSS_SELECTOR, 'a[data-test="anchor-pageNumber"]')
pages = max([int(page.get_attribute('data-test-page-number')) for page in pages])


def all_variables_filled(*args):
    return all(bool(arg) for arg in args)

job_offers = []

for i in range(1, int(pages) + 1):
    print("Page number: ", i)
    driver.get(f'https://theprotocol.it/filtry/1;s?pageNumber={i}')
    main_window = driver.current_window_handle
    driver.switch_to.window(main_window)

    for window_handle in driver.window_handles:
        if window_handle != main_window:
            driver.switch_to.window(window_handle)
            driver.close()

    driver.switch_to.window(main_window)
    driver.maximize_window()

    listings = driver.find_elements(By.CSS_SELECTOR, 'a[data-test="list-item-offer"]')
    wait = WebDriverWait(driver, 10)
    for listing in listings:
        while True:
            try:
                salaries = []
                technologies = []
                try:
                    driver.execute_script("arguments[0].scrollIntoView();", listing)
                except StaleElementReferenceException:
                    print("Element is not attached to the page document")
                    break
                offer_name = listing.get_attribute('aria-label')
                href = listing.get_attribute('href')
                from selenium.webdriver.common.keys import Keys
                main_window = driver.current_window_handle
                driver.execute_script("window.open();")
                driver.switch_to.window(driver.window_handles[1])
                try:
                    driver.get(href)
                    positionLevels = driver.find_element(By.CSS_SELECTOR, 'div[data-test="section-positionLevels"]')
                    seniority = positionLevels.find_element(By.CSS_SELECTOR, 'div[class="rootClass_rpqnjlt body1_b1gato5c initial_i1m6fsnc"]').text
                    # time.sleep(1)
                except Exception as e:
                    pass
                driver.switch_to.window(main_window)
                try:
                    listing.find_element(By.CSS_SELECTOR, 'span[aria-label="Przycisk do rozwijania i zwijania listy"]').click()
                except:
                    pass
                for salary_info in listing.find_elements(By.CLASS_NAME, 'textWrapper_t3j9udu'):
                    salary_bold_text = salary_info.find_element(By.CLASS_NAME, 'boldText_b1wsb650').text
                    salary_main_text = salary_info.find_element(By.CLASS_NAME, 'mainText_m15w0023').text
                    salaries.append(salary_bold_text + salary_main_text)
                company = listing.find_element(By.CSS_SELECTOR, 'div[data-test="text-employerName"]').text
                work_modes = listing.find_element(By.CSS_SELECTOR, 'div[data-test="text-workModes"]').text
                office_location = listing.find_element(By.CSS_SELECTOR, 'div[data-test="text-workplaces"]').text
                if "Oferta w wielu lokalizacjach" in office_location or "Multiple locations offer" in office_location:
                    office_location = []
                    for location in listing.find_elements(By.CSS_SELECTOR, "div[data-test='chip-location'] span"):
                        office_location.append(location.text)
                try:
                    whole_poland = listing.find_element(By.CSS_SELECTOR, 'div[data-test="text-whole-poland"]').text
                except:
                    pass
                try:
                    reveal_technologies_button = listing.find_element(By.CLASS_NAME,
                                                                      'spanClass_sv66w3q iconWrapperClass_i1i5a5y7').click()
                    # time.sleep(1)
                except:
                    pass
                for technology in listing.find_elements(By.CSS_SELECTOR, 'div[data-test="chip-expectedTechnology"] span'):
                    technologies.append(technology.text)
                if all_variables_filled(offer_name, salaries, company, work_modes, office_location):
                    job_offer = JobOffer(offer_name=offer_name, salaries=salaries, company=company, work_modes=work_modes,
                                         office=office_location, whole_poland=whole_poland, technologies=technologies, seniority=seniority)
                    job_offers.append(job_offer.to_dict())
                    print(job_offer)
                    break
            except:
                break
        # time.sleep(1)
driver.quit()

import pandas as pd

df = pd.DataFrame(job_offers)
df.head()
df.to_csv('job_offersv8.csv', index=False)