import json
from bs4 import BeautifulSoup
from urllib.request import urlopen


def getSummary(soup):
    summary =soup.find_all("p", limit=2)
    sText =''
    for s in summary:
        sText+= s.get_text()
        sText+='<p>'
    return sText

def lambda_handler(event, context):
    url = 'https://en.wikipedia.org/wiki/Heidenheim_an_der_Brenz'
    response = urlopen(url)
    html = response.read()
    stringHTML = (str(html, 'utf-8'))   
    soup = BeautifulSoup(stringHTML, 'html.parser')
    
    html = getSummary(soup)
    return {
        'statusCode': 200,
        'body': html,
        "headers": {
        'Content-Type': 'text/html',
        }
    }
