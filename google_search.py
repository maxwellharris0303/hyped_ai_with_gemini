from time import sleep
import undetected_chromedriver as uc
from difflib import SequenceMatcher
from urllib.parse import urlparse, urlunparse
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
import urllib.parse
from openai import OpenAI
import os
from bs4 import BeautifulSoup
import extract_date
import extract_price
import stock_checker
from format_date import get_formatted_dates

import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

# title_text = "Presale The Stanley X LoveShackFancy Holiday Quencher | 20 OZ - Rosa Beaux Pink"


def search(title_text):
    sanitized_title_text = urllib.parse.quote_plus(title_text)
    options = uc.ChromeOptions()
    driver = uc.Chrome(version_main=130)
    driver.maximize_window()
    driver.get("https://www.google.com/search?q=" + sanitized_title_text)

    unwanted_links = [
        "google.com",
        "ebay.",
        "stockx.com",
        "instagram.com",
        "facebook.com",
        "reddit.com",
        "tiktok.com"
    ]

    search_result = driver.find_element(By.CSS_SELECTOR, "div[id=\"search\"]")

    hrefs = [element.get_attribute('href') for element in search_result.find_elements(By.TAG_NAME, 'a') if element.get_attribute('href') and element.get_attribute('href').startswith("http")]

    possible_links_unfiltered = [link for link in hrefs if not any(unwanted in link for unwanted in unwanted_links)]

    possible_links_unfiltered = list(set(possible_links_unfiltered))

    # Convert array to a comma-separated string
    hrefs_string = ", ".join(possible_links_unfiltered)


    prompt = (
        "Sort through the links. ONLY OUTPUT LINKS THAT COULD BE THE PRODUCT LINK MATCHING THE PRODUCT: "
        + title_text +
        " IF THERE ARE MULTIPLE LINKS YOU BELIEVE ARE POSSIBLE, YOU CAN INCLUDE MULTIPLE BUT ONLY OUTPUT LINKS, NO EXTRA WORDING: "
        + hrefs_string
    )
    client = OpenAI(
        api_key=os.environ["API_KEY"],
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )

    
    completion = client.chat.completions.create(
        model="gemini-1.5-flash",
        n=1,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    response_message = completion.choices[0].message.content  # Use .content to get the message
    print(response_message)
    
    # Splitting the content by " \n" and storing it in a list
    links_list = [link.strip() for link in response_message.split("\n") if link != ""]
    print("#############################")
    print("COMPLETED LIST:", links_list)
    print("#############################")
    result = []

    for link in links_list:
        driver.get(link)
        sleep(5)
        # Get the page source
        content = driver.page_source

        price_list = extract_price.get_result(content)
        release_dates = extract_date.get_result(content)
        stock_result = stock_checker.get_result(content)

        if price_list and stock_result:
            data = {
                "link": link,
                "price_list": price_list,
                "release_dates": get_formatted_dates(release_dates)
            }
            result.append(data)

    driver.quit()
    return result

# print(search("Presale The Stanley X LoveShackFancy Holiday Quencher | 20 OZ - Rosa Beaux Pink"))