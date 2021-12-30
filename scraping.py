# Import dependencies
import pandas as pd
import datetime as dt

# Import Splinter and BeautifulSoup
from splinter import Browser
from bs4 import BeautifulSoup as soup
from webdriver_manager.chrome import ChromeDriverManager

def scrape_all():
    # 1) Initialize the browser
    # 2) Create a data dictionary
    # 3) End the WebDriver and return the scraped data

    # Set the executable path and 
    # initialize the headless webdriver (Chrome browser in Splinter)
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)

    # Set the news title and paragraph variaibles
    news_title, news_paragraph = mars_news(browser)

    # Set a variable to hold a list of dictionaries with the URL string and title of each hemisphere image
    # returned from the function hemisphere_img()
    hemisphere_image_urls = hemisphere_img(browser)

    # Run all scraping functions and store results in dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now(),
        "hemispheres": hemisphere_image_urls
    }

    # Stop webdriver (end the automated browsing session) and return data
    browser.quit()
    return data


def mars_news(browser):
    # Visit the mars nasa news site
    url = 'https://redplanetscience.com'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    # Convert the browser html to a soup object
    html = browser.html
    news_soup = soup(html, 'html.parser')

    # Add try/except for error handling for scraping
    try:
        # Using "select_one" function, the first matching element returned will be a \<li /> element with a class of "slide" and all nested elements within it.
        slide_elem = news_soup.select_one('div.list_text')

        # Use the parent element to find the first `a` tag and save it as `news_title`
        news_title = slide_elem.find('div', class_='content_title').get_text()

        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()
    
    except AttributeError:
        return None, None
    # Return the news title and paragraph
    return news_title, news_p

# ## JPL Space Images Featured Image
def featured_image(browser):
    # Visit URL
    url = 'https://spaceimages-mars.com'
    browser.visit(url)

    # Find the element by the tag 'button', and we want the second button which the the "FULL IMAGE" button
    full_image_elem = browser.find_by_tag('button')[1]
    # Click the button
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        # Find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')
    
    except AttributeError:
        return None
    
    # Use the base URL to create an absolute URL
    img_url = f'https://spaceimages-mars.com/{img_url_rel}'

    return img_url

# ## Mars Facts
def mars_facts():
    # Add try/except for error handling
    try:
        # Use 'read_html' to scrap the facts table into a DF
        # read_html() specifically search for and returns a list of 'tables' found in the HTML
        # with index of 0 --> pull only the first table found
        df = pd.read_html('https://galaxyfacts-mars.com')[0]

    except BaseException:
        return None
    
    # Assign columns and set index of dataframe
    df.columns=['description', 'Mars', 'Earth']
    df.set_index('description', inplace=True)

    # Convert DF back into HTML format, add table-hover using bootstrap
    # return df.to_html()
    return df.to_html(classes="table table-hover")

# ## Hemisphere Data
def hemisphere_img(browser):
    # Visit the hemisphere images site 
    url = 'https://marshemispheres.com/'
    browser.visit(url)

    # Create a list to hold the images and titles.
    hemisphere_image_urls = []

    # Write code to retrieve the image urls and titles for each hemisphere.
    for x in range(4):
        # Find and click on each hemisphere link
        page_to_image_elem = browser.find_by_tag('img.thumb')[x]
        page_to_image_elem.click()
        
        # Parse the resulting html (the full-resolution image page) with soup
        html = browser.html
        img_soup = soup(html, 'html.parser')
        
        # Add try/except for error handling for scraping
        try:
            # Get (1) full-resolution image URL string, and (2) title for the hemisphere image
            # (1) Find the 'Sample' image anchor tag, and get the href
            img_url_rel = img_soup.find('a', target='_blank', text='Sample').get('href')
            # Use the base url to create an absolute url
            img_url = f'{url}{img_url_rel}'
            
            # Find the h2 tag with class "title", and get the text
            title = img_soup.find('h2', class_='title').get_text()
        except AttributeError:
            return None

        # Create a dictionary to hold the scraped url and title
        hemispheres = {}
        hemispheres["img_url"] = img_url
        hemispheres["title"] = title
        # Append the hemispheres dictionary to the result list hemisphere_image_urls
        hemisphere_image_urls.append(hemispheres)

        # Navigate back to the beginning to get the next hemisphere image
        browser.back()

    # Return a list that holds the dictionary of each image url and title.
    return hemisphere_image_urls



if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())