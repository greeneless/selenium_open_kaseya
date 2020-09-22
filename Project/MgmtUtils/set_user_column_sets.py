from json import load
from time import sleep, time
from selenium.common.exceptions import NoSuchElementException
from Project.functions import agent, agent_procedures, logout
from Project.main import main, driver

# Program
start_time = time()
program_name = 'set_user_column_sets'

# No data? don't bother
try:
    with open('C:\\temp\\column_sets.json', 'r') as data:
        json = load(data)
except FileNotFoundError:
    print('Column_sets.json is missing from c:\\temp!')
    print('Run get_user_column_sets to generate this file from VSA user data.')
    exit(13)
else:
    pass


if __name__ == "__main__":
    main(web_driver_object=driver)

# Control menu
driver.find_element_by_xpath(agent_procedures(driver)).click()
sleep(2)

# Primary menu
driver.find_element_by_xpath(agent(driver)).click()
sleep(4)

# Access column sets - Manage
driver.find_element_by_xpath('//span/span/span[text()="Column Sets"]').click()
driver.find_element_by_xpath('//div[6]/a/span').click()

# New column set for each data object
for column_set in json:
    driver.find_element_by_xpath('//span/span/span[text()="New Column Set"]').click()
    sleep(3)
    print('Configuring column set: ' + column_set + '...')
    # Add to selection
    driver.find_element_by_xpath(
        '//table[1]/tbody/tr/td[2]/input[@name="columnsetname"]').send_keys(column_set)

    # Configure selection for each sub object dict
    for selection in json[column_set]:
        driver.implicitly_wait(0.5)
        try:
            # Click column name
            driver.find_element_by_xpath(
                '//span/div/div/div[2]/span/div/div/div/ul/li[text()="' + selection + '"]').click()
        except NoSuchElementException:
            print('Could not locate element for column header ' + selection)
            print('If referencing JSON source from another VSA, check for missing custom field')
        else:
            # Add to selection
            print('      adding selection: --' + selection + '...')
            driver.find_element_by_xpath('//tbody/tr/td[2]/div/div/div/div/div/div/a[3]/span/span/span[2]').click()
    driver.implicitly_wait(3)

    # Apply / Save
    driver.find_element_by_xpath('/html/body/div[17]/div[2]/div/div[2]/div/div/a[1]/span/span/span[2]').click()
    sleep(2)

# Exit
logout(driver)
print('Program ' + program_name + ' completed successfully.')
print("--- %s seconds ---" % (time() - start_time))
driver.quit()
exit(0)
