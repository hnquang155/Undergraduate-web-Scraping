from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
import time
import sys
import pandas as pd

success = False

input_ = str(input("Enter your course:"))

options = Options() # create an object of the Options class
options.add_argument("--window-size=1920,1080")
options.add_argument("--start-maximized")
options.add_argument("--headless")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),
                          options=options)

driver.get('https://www.uac.edu.au/course-search/undergraduate/find-a-course.html')
driver.maximize_window()

#print(f"Page title: {driver.title}.")


time.sleep(10)
#action for filter
filter = driver.find_element(by=By.ID, value="filterSectionInst")
action_filter = ActionChains(driver)
action_filter.click(on_element=filter)
action_filter.perform()

#find the checkbox of university
check_box = driver.find_elements(by=By.XPATH, value="//input[@ng-checked='USYD' or @ng-checked='WS' or @ng-checked='UNSW' or @ng-checked='UTS' or @ng-checked='MQ']")

#perform the filter of checkbox
for item in check_box:
    #print(item.text)
      
    action_checkbox = ActionChains(driver)
    action_checkbox.click(on_element=item)
    action_checkbox.perform()

    #time.sleep(2)

#find the search box
search = driver.find_element(by=By.ID, value="searchAnything") 

#send the input to search box and press enter
search.send_keys(input_)
search.send_keys(Keys.RETURN)

#create column variables for csv file
course_names = []
schools = []
locations = []
ATARs = []
assumed_knowledges = []
prerequisites = []
codes = []
count = 0

#search the open course
search_course = driver.find_elements(by=By.XPATH, value = "//div[@class = 'row course-container course-status-open  participating']")



#search "Show all" element and click if any
show_all_url = driver.find_element(by=By.XPATH, value = "//a[@class = 'showAlllink']")
try:
    show_all_url.click()
except:
    pass


#search the course again
search_course_repeat = driver.find_elements(by=By.XPATH, value = "//div[@class = 'row course-container course-status-open  participating']")

#filter the undergraduate course whoose duration is 3F
year_check = driver.find_elements(by=By.XPATH, value = "//*[@class = 'row course-container course-status-open  participating']//span[@class = 'poaValue ng-binding' and (starts-with(text(), '3F') or starts-with(text(), '3-'))]")
if (len(year_check)) == 0:
    print("No courses available")
    sys.exit()

for check in year_check:

    #extract code of the course
    code =  check.find_element(by=By.XPATH, value = "./preceding-sibling::span").text
    codes.append(code)

    #extract location of the course
    location = check.find_element(by=By.XPATH, value = "./ancestor::p[@class = 'courseCodePoa']/preceding-sibling::p[@class = 'course-location-campus mt-0']/a").text
    locations.append(location)

    #extract name of the course
    course = check.find_element(by=By.XPATH, value = ".//ancestor::div[@class = 'row course-container course-status-open  participating']//p[@class = 'course-name mt-0']/a")
    course_names.append(course.text)

    #get url 
    url = course.get_attribute('href')
    driver.execute_script("window.open('{}');".format(url))
  
    # Switch to the new window and open new URL
    driver.switch_to.window(driver.window_handles[1])

    #extract school name
    school = driver.find_elements(by=By.XPATH, value= '//p[@class="institution-name"]')[0]
    schools.append(school.text)
    #print(school.text)

    #extract assumed knowledge
    assumed_knowledge = driver.find_elements(by=By.XPATH, value="//div[@id = 'admission']/p")
    if assumed_knowledge:
        if assumed_knowledge[0].text.split(": ")[0] == "Assumed knowledge":
            assumed_knowledges.append(assumed_knowledge[0].text.split(": ")[1])
        else:
            assumed_knowledges.append(None)
    else:
        assumed_knowledges.append(None)
    #print(prequisite.text)

    #extract prerequisite
    prerequisite = driver.find_elements(by=By.XPATH, value="//div[@id = 'prereq']/p")
    if prerequisite:
        prerequisites.append(prerequisite[0].text)
    else:
        prerequisites.append(None)
    #print(prequisite.text)

    #ATAR Score
    ATAR = driver.find_elements(by=By.XPATH, value= "//table[@id = 'atarDataTable']/tbody/tr/th[text() = {}]/following-sibling::td".format(code))[0]
    ATARs.append(ATAR.text)

    #close tab
    driver.close()
    driver.switch_to.window(driver.window_handles[0])

#print(len(year_check))

time.sleep(5)
driver.close()

# print(len(course_names))
# print(len(codes))
# print(len(prerequisites))
# print(len(locations))
# print(len(assumed_knowledges))
# print(len(ATARs))
# print(len(schools))


df = pd.DataFrame({'Courses': course_names, "Code": codes, "Location": locations, "University": schools,
                    "Prequisites": prerequisites, "Assumed Knowledge": assumed_knowledges, "ATAR Score": ATARs})
df = df.sort_values(by = 'University').reset_index().drop(columns=['index'])
df.to_csv('Results.csv')
open('Results.csv', "r")
