# Dependencies
from bs4 import BeautifulSoup
from splinter import Browser
from selenium import webdriver
import pandas as pd
import requests


def init_browser():
    
    #Choose the executable path to driver
    executable_path = {'executable_path': '/usr/local/bin/chromedriver'}
    return Browser('chrome', **executable_path, headless=True)

def scrape_info():
    browser = init_browser()
    news_title, news_p = mars_news(browser)
    featured_image_url = mars_image(browser)
    mars_weather = mars_current_weather(browser)
    mars = mars_facts(browser)
    hemisphere_image_urls = mars_hemisphere(browser)

# Store data in a dictionary
    mars_data = {
        "news_title":news_title,
        "news_paragraph":news_p,
        "featured_image_url":featured_image_url,
        "mars_weather":mars_weather,
        "mars_facts":mars,
        "mars_hemisphere":hemisphere_image_urls
    }
    return mars_data


def mars_news(browser):
    # URL of page to be scraped
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)

    # Retrieve page with the requests module
    response = requests.get(url)
    # Create BeautifulSoup object; parse with 'lxml'
    soup = BeautifulSoup(response.text, 'lxml')
    try:
        # results are returned as an iterable list
        results = soup.find('div', class_='features')

        # Identify and return title of listing
        news_title = results.find('div', class_='content_title').a.text
        # Identify and return paragraph
        news_p = results.find('div', class_='rollover_description_inner').text 

    except:
        return None, None
        # Print results
    return news_title, news_p  

def mars_image(browser):

    #Visit Mars Space Images through splinter
    space_url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(space_url)

    # Locate full image and click
    full_image_elem = browser.find_by_id('full_image')
    full_image_elem.click()

    # Find button obtain additional information
    browser.is_element_present_by_text('more info', wait_time=1)
    more_info_elem = browser.find_link_by_partial_text('more info')

    # Click more info button
    more_info_elem.click()

    # HTML object 
    html = browser.html
    # Create BeautifulSoup object; parse with 'lxml'
    img_soup = BeautifulSoup(html, 'html.parser')

    try:
        # Image URL 
        main_image_rel = img_soup.select_one('figure.lede a img').get("src")
        main_image_rel

        # Complete url for image
        featured_image_url = f"https://www.jpl.nasa.gov{main_image_rel}"
        featured_image_url

    except:
        return None, None
        # Print results
    return featured_image_url

def mars_current_weather(browser):

    # Visit Mars Twitter
    weather_url = 'https://twitter.com/marswxreport?lang=en'
    browser.visit(weather_url)

    # Retrieve page with the requests module
    response = requests.get(weather_url)
    # Create BeautifulSoup object; parse with 'lxml'
    weather_soup = BeautifulSoup(response.text, 'lxml')

    try:
        # Find all elements that contain tweets
        mars_tweets = weather_soup.find_all('div', class_='js-tweet-text-container')

        # Loop to retrieve Sol & Pressure
        for tweet in mars_tweets:
            mars_weather = tweet.find('p').text
            if 'Sol' and 'pressure' in mars_weather:
                #print(f' Mars weather is {mars_weather}')
                break
            else:
                pass      
    except:
        return None, None
        
        # Print results
    return mars_weather

def mars_facts(browser):
    # Visit Mars Facts
    facts_url = 'https://space-facts.com/mars/' 

    # Read facts 
    mars_facts = pd.read_html(facts_url)

    # Create df to receive Mars Facts
    mars = mars_facts[0]

    # Assign columns and index
    mars.columns = ['Mars Planet Profile', 'Value']
    mars.set_index('Mars Planet Profile', inplace=True)
    
    try:
        # Save html code
        mars.to_html()
        data = mars.to_dict(orient='records')

        #show df
        mars   
    except:
        return None, None
        
        # Print results
    return mars     

def mars_hemisphere(browser):
    # Visit html & find list of links for hemisphere
    hemisphere_url = 'http://web.archive.org/web/20181114171728/https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(hemisphere_url)
    links = browser.find_by_css("a.product-item h3")
    try:
        # loop through links
        hemisphere_image_urls =[]
        for i in range(len(links)):
            browser.visit(hemisphere_url)
            browser.find_by_css("a.product-item h3")[i].click()
            # Next, we find the Sample image anchor tag and extract the href
            sample_elem = browser.find_link_by_text('Sample').first
            title = browser.find_by_css("h2.title").text
            img_url = sample_elem['href']
    
            hemisphere_image_urls.append({"title" : title, "img_url": img_url})
    
        hemisphere_image_urls

    # Close the browser after scraping
    #browser.quit()

    except:
        return None, None

    # Return results
    return hemisphere_image_urls    

if __name__ == "__main__":
    print(scrape_info())