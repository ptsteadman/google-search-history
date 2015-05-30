import datetime
import re
import sys
import time
import argparse
import json

import mechanize
from bs4 import BeautifulSoup

def select_form(browser, form_id):
    '''With a mechanize browser, selects a form based on id'''
    for form in browser.forms():
        if form.attrs.get('id') == form_id:
            browser.form = form
            break

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
    p = re.compile(r"(?<=window.HISTORY_response=)(.*?)(?=;window)")
    m = p.search(response.read())
    if m is None:
        return None
    hist_str = m.group()
    p = re.compile(r"(?<=,\[\[\")(.*?)(?=\")")
    m = p.findall(hist_str)
    for match in m:
        history.append(match)

def get_history(email, passwd, code=None):
    '''Get the google search history for a user.'''
    browser = mechanize.Browser()
    browser.set_handle_robots(False)
    if authenticate(browser, email, passwd, code):
        history = []
        get_page(browser, 'https://history.google.com/history', history)
        return history

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Search tweeter")
    parser.add_argument("username", help="Google username")
    parser.add_argument("password", help="Google password")
    parser.add_argument("--code", help="Google second factor auth code")
    args = parser.parse_args()

    history = get_history(args.username, args.password, args.code)
    if len(history) > 0:
        for search in history:
            print search
    else:
        print "Error getting searches."
