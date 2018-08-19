import pandas as pd
from bs4 import BeautifulSoup
from splinter import Browser
from selenium import webdriver
import time
import requests
import shutil
import tweepy

consumer_key = "rWYwPO5GujlB2DJnYxuiFXpv0"
consumer_secret = "tkqWqUDNeGNCxHAgSPzObW88YKBxfxGazD3T0XWqH9aklACNiZ"
app_key = "891138909161242624-brnipgrui4Zl2ygfbVIrwc5OwEwRGIN"
app_secret = "yajiQuWe5ux8hxU2xjgb7ZBAM6LHEzL8NnUpmgrNziAom"

def init_browser():
    executable_path = {"executable_path": "/Applications/chromedriver"}
    return Browser("chrome", **executable_path, headless=False)

def scrape():
    browser = init_browser()

    mars_data = {}
    url1 = "https://mars.nasa.gov/news/?page=0&per_page=40&order=publish_date+desc%2Ccreated_at+desc&search=&category=19%2C165%2C184%2C204&blank_scope=Latest"
    url2 = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    url3 = "https://space-facts.com/mars/"
    url4 = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"

    browser.visit(url1)

    # Page into soup
    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')

    article = soup.find("div", class_="list_text")
    news_p = article.find("div", class_="article_teaser_body").text
    news_title = article.find("div", class_="content_title").text
    news_date = article.find("div", class_="list_date").text
    mars_data["news_date"] = news_date
    mars_data["news_title"] = news_title
    mars_data["summary"] = news_p

    browser.visit(url2)

    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')
    image = soup.find("img", class_="thumb")["src"]
    img_url = "https://jpl.nasa.gov"+image
    featured_image_url = img_url
    mars_data["featured_image_url"] = featured_image_url

    #Tweepy API Authentication
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(app_key, app_secret)
    api = tweepy.API(auth, parser=tweepy.parsers.JSONParser())

    target_user = "marswxreport"
    full_tweet = api.user_timeline(target_user , count = 1)
    mars_weather=full_tweet[0]['text']
    mars_data["mars_weather"] = mars_weather

    browser.visit(url3)
    grab=pd.read_html(url3)
    mars_info=pd.DataFrame(grab[0])
    mars_info.columns=['Mars','Data']
    mars_table=mars_info.set_index("Mars")

    marsinformation = mars_table.to_html(classes='marsinformation')
    marsinformation =marsinformation.replace('\n', ' ')

    mars_data["mars_table"] = marsinformation

    browser.visit(url4)
    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')
    mars_hemis=[]

    for i in range (4):
        time.sleep(5)
        images = browser.find_by_tag('h3')
        images[i].click()
        html = browser.html
        soup = BeautifulSoup(html, 'html.parser')
        partial = soup.find("img", class_="wide-image")["src"]
        img_title = soup.find("h2",class_="title").text
        img_url = 'https://astrogeology.usgs.gov'+ partial
        dictionary={"title":img_title,"img_url":img_url}
        mars_hemis.append(dictionary)
        browser.back()

    mars_data['mars_hemis'] = mars_hemis

    return mars_data