from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import pymongo as mongo
from bs4 import BeautifulSoup
import pandas as pd


def scraping():
    # Loading Selenium Webdriver
    # driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    service = Service(executable_path="chromedriver.exe")
    driver = webdriver.Chrome(service=service)
    # Opening Google maps
    driver.get("https://www.google.com/maps")
    time.sleep(3)

    # Finding the search box
    searchbox = driver.find_element(By.ID, 'searchboxinput')
    location = input("Please enter a location/business: ")
    searchbox.send_keys(location)
    searchbox.send_keys(Keys.ENTER)
    time.sleep(10)
    # retrieving the page source
    source = driver.page_source

    business_details_list = []
    # scraping using Beautiful Soup
    soup = BeautifulSoup(source, 'html.parser')
    results = soup.find_all('div', attrs={'class': "bfdHYd Ppzolf OFBs3e"})
    for result in results:
        name = result.find('div', attrs={'class': 'qBF1Pd fontHeadlineSmall'}).get_text()
        try:
            address = result.find('div', attrs={'class': "UaQhfb fontBodyMedium"}).find_all('div', attrs={'class': "W4Efsd"})[
                    1].find_all("span")[2].get_text()
        except AttributeError and IndexError:
            address = "No Address found"
        try:
            category = result.find('div', attrs={'class': "UaQhfb fontBodyMedium"}).find_all('div', attrs={'class': "W4Efsd"})[
                    1].find_all("span")[0].get_text()
        except AttributeError and IndexError:
            category = "No category found"
        try:
            review_average = result.find('span', attrs={'class': 'MW4etd'}).get_text()
        except AttributeError:
            review_average = "No Reviews found"
        try:
            review_count = result.find('span', attrs={'class': "UY7F9"}).get_text()
        except AttributeError:
            review_count = "No Reviews found"
        try:
            webcontainer = result.find('a', attrs={'class': 'lcr4fd S9kvJb', 'href': True})
            website = webcontainer["href"]
        except TypeError:
            website = "No website found"

        try:
            phone = result.find('span', attrs={'class': "UsdlK"}).get_text()
        except AttributeError:
            phone = "No phone number found"

        business_details = {
            'Business_name': name,
            'Address': address,
            'Category': category,
            'Review_average': review_average,
            'Review_count': review_count,
            'Website': website,
            'Phone_number': phone
        }
        business_details_list.append(business_details)
    df = pd.DataFrame(business_details_list)
    # print(df)
    return df


def main():
    scraped_data = scraping()
    # print(scraped_data)
    try:
        client = mongo.MongoClient("mongodb://localhost:27017")
        db = client.get_database("googleMapScrapper")
        collection = db.get_collection("Results2")

        data = scraped_data.to_dict(orient='records')
        collection.insert_many(data)
        print("Data is inserted in the database")
    except Exception as e:
        print("The program has run into some Exception while connection to the database or inserting the data to the database", e)


# Entry point of the program
if __name__ == "__main__":
    main()
