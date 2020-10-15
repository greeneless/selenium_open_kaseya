from json import dumps
from time import sleep, time
from selenium.common.exceptions import ElementClickInterceptedException
from Project.functions import agent, agent_procedures, logout
from Project.main import main, driver

if __name__ == '__main__':
    main(web_driver_object=driver)

# Program
start_time = time()
program_name = 'get_user_column_sets'

# Control menu
driver.find_element_by_xpath(agent_procedures(driver)).click()
sleep(2)

# Primary menu
driver.find_element_by_xpath(agent(driver)).click()
sleep(4)

# Access column sets - Manage
driver.find_element_by_xpath('//span/span/span[text()="Column Sets"]').click()
driver.find_element_by_xpath('//div[6]/a/span').click()
sleep(1.5)

print('Reading current user columns...')
column_set_objects = driver.find_elements_by_xpath(
    '//span/div/div/div[3]/div/div[3]/div/table/tbody/tr[*]/td[2]/div/div')

# Save the name of the sets
column_sets_data = {}
for element in column_set_objects:
    print('Found column set: ' + element.text)
    element.click()
    driver.find_element_by_xpath(
        '//div/div/a[2]/span/span/span[text()="Edit Column Set"]').click()
    sleep(2)

    # Assign column set data and selection to JSON/Dict
    selected_objects = driver.find_elements_by_xpath(
        '//span/div/table[2]/tbody/tr/td[2]/div/table/tbody/tr/td[2]/div/div/div/' +
        'table[2]/tbody/tr/td[2]/div/span/div/div/div[2]/span/div/div/div/ul/li')
    selected = {item.text: 1 for item in selected_objects}
    column_sets_data.update({element.text: selected})

    # Testing on two different VSA versions revealed inconsistent div index for [check]
    for ref in reversed(range(30)):
        # Disable implicit wait
        driver.implicitly_wait(0)
        # Throw darts until match
        check = driver.find_elements_by_xpath(
            '/html/body/div[' + str(ref) + ']/div[2]/div/div[2]/div/div/a[2]/span/span/span[2]')
        if check:
            try:
                check[0].click()
            except ElementClickInterceptedException:
                print('Unable to click XPATH /html/body/div[' + str(ref) +
                      ']/div[2]/div/div[2]/div/div/a[2]/span/span/span[2]')
            else:
                try:
                    sleep(1)
                    element.click()
                except ElementClickInterceptedException:
                    print('Improper button clicked, window not canceled')
                else:
                    break
        # else:
        #     print('No matching element for XPATH /html/body/div[' + str(ref) +
        #           ']/div[2]/div/div[2]/div/div/a[2]/span/span/span[2]')
driver.implicitly_wait(3)

# Dump column sets JSON contents below
json = dumps(column_sets_data, indent=2)

# Write formatted objects to file
print('Writing column_set objects to c:\\temp\\column_sets.json. If a file match is present, overwriting...')
f = open('c:\\temp\\column_sets.json', 'w')
f.write(json)
f.close()
sleep(1)

# Exit
print('Logging out current user...')
logout(driver)
print('Program ' + program_name + ' completed successfully.')
print("--- %s seconds ---" % (time() - start_time))
driver.quit()
exit(0)
