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

    # write synopsis direct to DB
    import psycopg2

    # Connect to an existing database
    # FIXME source from heroku props
    conn = psycopg2.connect("dbname='" + os.environ['DB_NAME'] + "' user='" + os.environ['DB_USER'] + "' host='" + os.environ['DB_HOST'] + "' password='" + os.environ['DB_PASSWORD'] + "' sslmode='require'")
    
    # Open a cursor to perform database operations
    cur = conn.cursor()
    
    # Pass data to fill a query placeholders and let Psycopg perform
    # the correct conversion (no more SQL injections!)
    cur.execute("INSERT INTO public.\"SummaryText\" (isbn, oauthid, datetime, text) VALUES (%s, %s, %s, %s) RETURNING id",(asin, '99991', 'now()', decodedBookDescription))
    insertIdAmaznon = cur.fetchone()[0]
    cur.execute("INSERT INTO public.\"SummaryText\" (isbn, oauthid, datetime, text) VALUES (%s, %s, %s, %s) RETURNING id",(asin, '99992', 'now()', wsBookDescription))
    insertIdWaterstones = cur.fetchone()[0]
    
    # Make the changes to the database persistent
    conn.commit()
    
    # Close communication with the database
    cur.close()
    conn.close()

    jsonData = {
        "URL":url,
        "SynopsisAmazon":decodedBookDescription,
        "SynopsisWaterstones":wsBookDescription,
        "SynopsisIdAmazon":insertIdAmaznon,
        "SynopsisIdWaterstones":insertIdWaterstones

    }

    response = HttpResponse(json.dumps(jsonData), content_type="application/json")
    response['Access-Control-Allow-Origin'] = '*'
    return response