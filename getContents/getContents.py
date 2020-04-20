import json
from bs4 import BeautifulSoup, NavigableString, Tag
from urllib.request import urlopen
import re

def getTableOfContentsAsList(soup):
    tocList = []
    x= soup.find_all("span", class_="toctext")
    for t in x:
        tocList.append(t.get_text())
    return tocList
    
def getTableOfContentsAsText(soup):
    tocText = '<ul>'
    x= soup.find_all("span", class_="toctext")
    for t in x:
        tocText+= '<li>'+t.get_text()
    tocText+='</ul>'
    return tocText
    
def getSectionText(sectionName, soup):
    sectionText = ''
    sectionName = sectionName.replace(' ', '_')
    section = soup.find(id=sectionName)
    
    if(section == None):
        return sectionText
    
    sectionText += sectionName+"\n"
    
    #Find the header number for this section
    secHeader= section.find_previous(re.compile('^h[1-6]$'))
    secHeaderNumber = secHeader.name[1]
    #Create a regex that will match headers to this level and above
    #Ex: if this section is h3, we want to break at the next h3 or h2
    secMatchRegex = f"^h[1-{secHeaderNumber}]$"
    headerMatcher = re.compile(secMatchRegex)

    #Return all HTML nodes of interest under this section
    nextNode = secHeader.next_element
    while nextNode:
        if isinstance(nextNode, Tag):
           if nextNode.name =="p":
                sectionText+= str(nextNode)
           if nextNode.name == "ul":
                sectionText += str(nextNode)
           if nextNode.name == "li":
                sectionText += str(nextNode)
           if nextNode.name == "table":
                sectionText += str(nextNode)
           if headerMatcher.match(nextNode.name):
                break
        nextNode = nextNode.next_element
    
    return sectionText
    
def lambda_handler(event, context):
    url = 'https://en.wikipedia.org/wiki/Heidenheim_an_der_Brenz'
    response = urlopen(url)
    html = response.read()
    stringHTML = (str(html, 'utf-8'))
    soup = BeautifulSoup(stringHTML, 'html.parser')
    
    #Get table of contents
    tocList = getTableOfContentsAsList(soup);
    
    html=''
    statusCode = 200
    if 'queryStringParameters' in event:
        query = event['queryStringParameters']
        if 'content' in query:
            contentName = str(query['content'])
            if contentName in tocList:
                html=getSectionText(contentName, soup)
            else:
                statusCode = 400
                html =f"Bad Request. Section name '{contentName}' is not a valid content section option."
        else:
            statusCode = 400
            html =f"Bad Request. Parameters provided are not recognized"

    else:
        html = getTableOfContentsAsText(soup)
    return {
        'statusCode': statusCode,
        'body': html,
        "headers": {
        'Content-Type': 'text/html',
        }
    }