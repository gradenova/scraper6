from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from bs4 import BeautifulSoup

def index(request):

    import json  
    import requests
    import re
    import urllib2
        
    #url = "http://www.amazon.co.uk/Nineteen-Eighty-Four-Penguin-Modern-Classics/dp/014118776X"
    url = request.GET.get('url', '')
    asin = request.GET.get('asin', '')
    isbn = request.GET.get('isbn', '')

    headers = {'user-agent': 'my-app/0.0.1'}
    page = requests.get(url, headers=headers)
    html_contents = page.text
    soup = BeautifulSoup(html_contents, 'html.parser')
    
    scriptText = ''
    for s in soup.find_all('script'):
        scriptText += s.getText()

    p = re.compile('bookDescEncodedData = "(.*?)",')
    m = p.search(scriptText)
    
    bookDescription = m.group(1)
    
    decodedBookDescription = urllib2.unquote(bookDescription).decode("utf-8", "strict")

    #Waterstones
    url = "https://www.waterstones.com/book/" + isbn
    page = requests.get(url, headers=headers)
    wsBookDescription = 'null'
    if(page.status_code == 404):
        print("404! Skipping ISBN : " + isbn)
    else:
        html_contents = page.text
        soup = BeautifulSoup(html_contents, 'html.parser')
        
        if(soup.find("div", id="scope_book_description")):
            wsBookDescription = soup.find("div", id="scope_book_description").text.strip()

    jsonData = {
        "URL":url,
        "SynopsisAmazon":decodedBookDescription,
        "SynopsisWaterstones":wsBookDescription,
        "SynopsisIdAmazon":'1',
        "SynopsisIdWaterstones":'2'

    }

    response = HttpResponse(json.dumps(jsonData), content_type="application/json")
    response['Access-Control-Allow-Origin'] = '*'
    return response