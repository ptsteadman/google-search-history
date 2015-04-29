'''Search Tweeter

Usage:
    python search_tweeter.py statefile email passwd [code]

    where `code` is used for second factor authentication.
'''

import datetime
import re
import sys
import time

import mechanize
import twitter
from bs4 import BeautifulSoup


def select_form(browser, form_id):
    '''With a mechanize browser, selects a form based on id'''
    for form in browser.forms():
        if form.attrs.get('id') == form_id:
            browser.form = form
            break

def descend(node, path):
    '''Traverse a beautifulsoup node downwards according to
    a specific path.
    descend(node, [0, 1]) => node.contents[0].contents[1]
    '''
    for i in path:
        if len(node.contents) <= i:
            return None
        node = node.contents[i]
    return node

def authenticate(browser, email, passwd, code=None):
    '''Authenticate a google user based on the supplied credentials'''
    attempt_first_factor(browser, email, passwd)
    if failed_first_factor(browser):
        sys.exit("Incorrect email and password combination")
    if requires_second_factor(browser):
        attempt_second_factor(browser, code)
        if failed_second_factor(browser):
            sys.exit("Second factor failed")
    return True

def attempt_first_factor(browser, email, passwd):
    '''Attempt a email/password challange'''
    response = browser.open('https://history.google.com')
    select_form(browser, 'gaia_loginform')
    browser['Email'] = email
    browser['Passwd'] = passwd
    return browser.submit()

def attempt_second_factor(browser, code):
    '''Attempt to second factor authentication code challenge'''
    select_form(browser, 'gaia_secondfactorform')
    browser['smsUserPin'] = code
    return browser.submit()

def requires_second_factor(browser):
    '''Check to see if second factor authentication'''
    return 'SecondFactor' in browser.response().geturl()

def failed_first_factor(browser):
    '''Check to see if first factor authentication was unsuccessful'''
    return 'ServiceLoginAuth' in browser.response().geturl()

def failed_second_factor(browser):
    '''Check to see if second factor authentication was unsuccessful'''
    return 'SecondFactor' in browser.response().geturl()

def parse_time(time):
    '''Convert a time from "3:36pm" to "15:36"'''
    pm = time[-2:] == 'pm'
    time = time[:-2].split(':')
    hours = int(time[0])
    mins = int(time[1])
    if pm:
        hours += 12
    return '{:02d}:{:02d}'.format(hours, mins)

def parse_date(date):
    '''Convert a date from "14 Jan" or "14 Jan, 2013" to :2013-01-14"'''
    if date == 'Today':
        return datetime.date.today().isoformat()
    elif date == 'Yesterday':
        yesterday = datetime.date.today() - datetime.timedelta(1)
        return yesterday.isoformat()
    else:
        date = date.replace(' ', '')
        date = date.split(',')
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        month = months.index(date[0][:3]) + 1
        day = int(date[0][3:])
        year = datetime.date.today().year
        if len(date) == 2:
            year = int(date[1])
        return datetime.date(day=day, month=month, year=year).isoformat()

def get_page(browser, url, history):
    '''Get all searches from a page and return the URL to the next page.'''
    response = browser.open(url)
    soup = BeautifulSoup(response.read())
    search_date = parse_date('Today')
    for i in xrange(0, 36):
	row = soup.select("#r" + str(i))
	if len(row) > 0:
	    search = row[0].select("a")[0].text
            history.append(search)

    # Determine the URL for the next page, if there is a next page
    buttons = soup.find_all('a', attrs={'class': 'kd-button'})
    for button in buttons:
        if button.text == 'Older':
            return button.attrs.get('href')

def get_history(email, passwd, code=None):
    '''Get the google search history for a user.'''
    browser = mechanize.Browser()
    browser.set_handle_robots(False)
    if authenticate(browser, email, passwd, code):
        history = []
	get_page(browser, 'https://history.google.com/history', history)
        return history

def tweet(api, message):
    api.PostUpdate(message)

if __name__ == '__main__':
    argc = len(sys.argv)
    if argc < 5 or argc > 6:
        sys.exit('Usage: python search_tweeter.py tweet statefile email passwd [code]')

    outfile = sys.argv[1]
    tweet = sys.argv[2]
    email = sys.argv[3]
    passwd = sys.argv[4]
    code = None
    if argc == 6:
        code = sys.argv[5]

    if tweet:
	api = twitter.Api(consumer_key='',
			  consumer_secret='',
			  access_token_key='',
			  access_token_secret='')

    history = get_history(email, passwd, code)
    if len(history) > 0:
	try:
	    most_recent = None
	    with open(outfile, 'r') as f:
		most_recent = f.readline()
		new_most_recent = history[0]

	    to_tweet = []
	    for search in history:
		if search == most_recent:
		    break
		else:
		    to_tweet.append(search)

	except IOError as e:
	    print "Creating 'most recent' file."
	    to_tweet = [history[0]]
	    new_most_recent = history[0]

    else:
	print "Error getting searches."

    for message in reversed(to_tweet):
	print message
	if tweet:
	    tweet(api, message)
	    time.sleep(5)

    with open(outfile, 'w') as f:
	f.write(new_most_recent)

