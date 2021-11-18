import re
from urllib.parse import urlparse
import urllib
import sys
from collections import defaultdict
from lxml import html
import numpy as np
from bs4 import BeautifulSoup as bs
import pickle
from collections import defaultdict

numWords = 0

def scraper(url, resp):

    if not handlingErrors(url, resp):
        return list()

    if resp.raw_response.is_redirect:
        if not is_valid(resp.raw_response.history[-1].url):
            return list()

    if resp.raw_response.content == '':
        return list()

    # try:
    #     soup = bs(resp.raw_response.content, 'html.parser')
    #     data1 = soup.get_text()
    #     with open('words.txt','r') as file:
    #         data2 = file.read()
    #         if data2 in data1:
    #             return list()
    # except FileNotFoundError:
    #     pass
    q1(url)
    links = extract_next_links(url, resp)
    valid = list()
    for link in links:
        if is_valid(link):
            valid.append(link)

    return valid


def extract_next_links(url, resp):
    data = html.fromstring(resp.raw_response.content)
    url = re.sub(u'[^\u0020-\uD7FF\u0009\u000A\u000D\uE000-\uFFFD\U00010000-\U0010FFFF]+', '', url)
    data.make_links_absolute(base_url = url)
    
    links = list()
    for link in data.iterlinks():
        link = urllib.parse.urldefrag(link[2])[0]
        links.append(link)

    q2(resp.raw_response.content, url)

    return links

def is_valid(url):
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        if re.search("\d{4}-\d{2}(-\d{2})?", url):
            return False
        if re.search("/calendar/\d{4}/\d{2}(/\d{2})?", url):
            return False
        if re.search("archive.ics.uci.edu/ml", url):
            return False
        if re.search(".pdf|.png|.jpg|.doc|.docx|.pptx|.tiff", url):
            return False
        if re.search("https://www.ics.uci.edu/alumni/stayconnected", url):
            return False
        if re.search("\?share", url):
            return False
        if re.search("format=xml", url):
            return False
        if re.search("\?action=", url):
            return False
        if re.search("\?url=", url):
            return False
        if re.search("www.informatics.uci.edu/?p=3252", url):
            return False
        if re.search("https://www.ics.uci.edu/ugrad/courses/index", url):
            return False
        if re.search(".Thesis", url):
            return False
        if re.search("http://swiki.ics.uci.edu/doku.php/start?do=diff", url):
            return False

        return (not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())) and\
        re.search(".ics.uci.edu/|.cs.uci.edu/|.informatics.uci.edu/|.stat.uci.edu/|today.uci.edu/department/information_computer_sciences/",url)

    except TypeError:
        print ("TypeError for ", parsed)
        raise

def handlingErrors(url, resp):
    if resp.status >= 600:     #caching errors
        return False
    if 599 >= resp.status >= 400: #Server and Client errors
        return False
    return True

def q1(url):
    try:
        file = np.load('unique.npy')
        file = np.append(file, [url])
        np.save('unique.npy', file)

    except IOError:
        file = np.array([url])
        np.save('unique.npy', file)

def q2(html, url):
    soup = bs(html, 'html.parser')
    data = soup.get_text()

    numWords = len(data)

    try:
        file = open('longestPage.txt','r')
        oldnumWords = file.read().split()[0]
        if int(oldnumWords) < int(numWords):
            file.close()
            file = open('longestPage.txt','w')
            file.write((str(numWords) + " " + url))
        file.close()
    except FileNotFoundError:
        with open('longestPage.txt','w') as file:
            file.write((str(numWords) + " " + url))
            file.close()

    try:
        with open('words.txt','a') as file:
            file.write(data)
            file.close()
    except FileNotFoundError:
        with open('words.txt','w') as file:
            file.write(data)
            file.close()

"""
Runtime complexity: O(N)
I just iterate over the file once. Hence, the runtime is O(N)
"""
def tokenize(data):
    lstToken = list()
    token = ''

    for i in data:
        if re.search('_*\w_*', i):
            token += i
        elif token == '':
            continue
        else:
            lstToken.append(token.lower())
            token = ''

    return len(lstToken)
