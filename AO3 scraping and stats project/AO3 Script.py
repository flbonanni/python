# -*- coding: utf-8 -*-
"""
Created on Tue Feb 28 20:04:13 2023

@author: flavia bonanni
"""

##################### WARNING #####################
# this script needs ChromeDriver to work
# before starting, set the path to the ChromeDriver on your machine
# then choose a user to analyse (a random user is provided as an example)

# set the path to the ChromeDriver
path = "C:/Users/flbon/OneDrive/Desktop/Boolean/chromedriver_win32/" 

# set user
user = 'Im_Chamsae'

from selenium import webdriver
from selenium.webdriver.common.by import By
from pygrok import Grok
import pandas as pd
import time

##################### FUNCTIONS #####################

# puts all works from a page in a list
# each element of the list is a work
# inside the work, each line is a different element
# line 0 is title, line 6 is date, the stats line is 8 or 9
def get_works_list():
    raw_data = driver.find_elements(By.XPATH, value="//li[@role = 'article']")
    works_list = []
    for element in raw_data:
        works_list.append(element.text)
    return works_list

# extracts date, which is always 6th line
def extract_date(article):
    lines = article.splitlines()
    pattern = '%{MONTHDAY:day} %{MONTH:month} %{YEAR:year}'
    grok = Grok(pattern)
    dict_date = grok.match(lines[6])
    df = pd.DataFrame([dict_date])
    return df
    
# extracts title, which is always on the 0th line
def extract_title(article):
    lines = article.splitlines()
    return lines[0]

# extracts rating, which is always on the 2nd line
def extract_rating(article):
    lines = article.splitlines()
    return lines[2]

# extracts rating, which is always on the 1st line
def extract_fandom(article):
    lines = article.splitlines()
    return lines[1]

# extract stats by identifying on which line they are
# and using a grok pattern to turn them into a dictionary
# has exceptions for no bookmarks and no collections
def extract_stats(article):
    lines = article.splitlines()
    stats_line = 0
    index = 0
    for line in lines:
        if line.startswith("Language:"):
            stats_line = index
        else: index += 1
    stats = lines[stats_line]
    stats = stats.replace(",", "")
    if "Comments" in stats: 
        if "Collections" in stats:
            if "Bookmarks" in stats:
                pattern = 'Language: %{WORD:language} Words: %{NUMBER:words} Chapters: %{NUMBER:chapter_running_count}/%{NOTSPACE:chapter_total_count} Collections: %{NUMBER:collections} Comments: %{NUMBER:comments} Kudos: %{NUMBER:kudos} Bookmarks: %{NUMBER:bookmarks} Hits: %{NUMBER:hits}'
            else:
                pattern = 'Language: %{WORD:language} Words: %{NUMBER:words} Chapters: %{NUMBER:chapter_running_count}/%{NOTSPACE:chapter_total_count} Collections: %{NUMBER:collections} Comments: %{NUMBER:comments} Kudos: %{NUMBER:kudos} Hits: %{NUMBER:hits}'
        else:
            if "Bookmarks" in stats:
                pattern = 'Language: %{WORD:language} Words: %{NUMBER:words} Chapters: %{NUMBER:chapter_running_count}/%{NOTSPACE:chapter_total_count} Comments: %{NUMBER:comments} Kudos: %{NUMBER:kudos} Bookmarks: %{NUMBER:bookmarks} Hits: %{NUMBER:hits}'
            else:
                pattern = 'Language: %{WORD:language} Words: %{NUMBER:words} Chapters: %{NUMBER:chapter_running_count}/%{NOTSPACE:chapter_total_count} Comments: %{NUMBER:comments} Kudos: %{NUMBER:kudos} Hits: %{NUMBER:hits}'
    else:
        if "Collections" in stats:
            if "Bookmarks" in stats:
                pattern = 'Language: %{WORD:language} Words: %{NUMBER:words} Chapters: %{NUMBER:chapter_running_count}/%{NOTSPACE:chapter_total_count} Collections: %{NUMBER:collections} Kudos: %{NUMBER:kudos} Bookmarks: %{NUMBER:bookmarks} Hits: %{NUMBER:hits}'
            else:
                pattern = 'Language: %{WORD:language} Words: %{NUMBER:words} Chapters: %{NUMBER:chapter_running_count}/%{NOTSPACE:chapter_total_count} Collections: %{NUMBER:collections} Kudos: %{NUMBER:kudos} Hits: %{NUMBER:hits}'
        else:
            if "Bookmarks" in stats:
                pattern = 'Language: %{WORD:language} Words: %{NUMBER:words} Chapters: %{NUMBER:chapter_running_count}/%{NOTSPACE:chapter_total_count} Kudos: %{NUMBER:kudos} Bookmarks: %{NUMBER:bookmarks} Hits: %{NUMBER:hits}'
            else:
                pattern = 'Language: %{WORD:language} Words: %{NUMBER:words} Chapters: %{NUMBER:chapter_running_count}/%{NOTSPACE:chapter_total_count} Kudos: %{NUMBER:kudos} Hits: %{NUMBER:hits}'
    grok = Grok(pattern)
    return grok.match(stats)
    #return stats

##################### LAUNCH #####################

# initialise the driver (and open up a browser window)
driver = webdriver.Chrome(path + 'chromedriver.exe')

# open up a specific web page
driver.get("https://archiveofourown.org/users/" + user)

# get rid of TOS
time.sleep(10)
driver.find_element_by_id("tos_agree").click();
driver.find_element_by_id("accept_tos").click();

# move to 'works' webpage
driver.find_element(By.XPATH, value='//*[@id="user-works"]/ul[2]/li/a').click()

# get number of pages
pagination = driver.find_elements(By.XPATH, value='//*[@id="main"]/ol[1]')
pagination_elements = [col.text for col in pagination]
pages = pagination_elements[0].split(" ")
words_to_remove = ['←', 'Previous', 'Next', '→']
pages = [e for e in pages if e not in words_to_remove]
# exception for prolific authors
if "…" in pages:
    last = pages[-1]
    pages_temp = [None] * int(last)
    for p in range(len(pages_temp)):
        pages_temp[p] = p+1
    pages = map(str, pages_temp)

#build dataframe
data = pd.DataFrame()

for page in pages:
    if page != "1":
        driver.find_elements(By.LINK_TEXT, str(page))[0].click()
    works_list = get_works_list()
    for i in range(len(works_list)):
        title = extract_title(works_list[i])
        fandom = extract_fandom(works_list[i])
        rating = extract_rating(works_list[i])
        date = extract_date(works_list[i])
        stats = extract_stats(works_list[i])
        df_temp = pd.DataFrame([stats])
        df_temp['title'] = title
        df_temp['fandom'] = fandom
        df_temp['rating'] = rating
        df_temp['day'] = date['day']
        df_temp['month'] = date['month']
        df_temp['year'] = date['year']
        data = data.append(df_temp)



data.to_csv('data/ao3.csv', index=False)