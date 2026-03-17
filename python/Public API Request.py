## Create import request
import requests
from requests import get
from gazpacho import Soup
from requests import get

## install gazpacho on our machine
!pip install gazpacho

# social media website
url = "https://alexwohlbruck.github.io/cat-facts/"

# request content
response = get("https://alexwohlbruck.github.io/cat-facts/")
print(response.status_code)

if response.status_code == 200: 
    print("200: get data ok")
else:
    print("please check your url again.")

# transform to soup object
web = get(url)
wsc = Soup(web.text)
print(type(wsc))

# extract heading 2 on the website 
wsc.find("h2".strip())

# Find the heading 2 for all elements on the website 
for h2 in wsc.find("h2"):
    print(h2.strip())


# Find the heading 3 for all elements on the website
for h3 in wsc.find("h3"):
    print(h3.strip())


# extract paragraphs on the website 
for paragraphs in wsc.find("p"):
    print(paragraphs.text)


# extract link on the website 
for link in wsc.find("a"):
    print(link.strip())
