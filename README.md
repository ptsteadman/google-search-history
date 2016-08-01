# Google Search Tweeter

Really hacky script that tweets everything that you google.

This code is essentially deprecated because Google changed the [history page](https://history.google.com)
to an AngularJS application.  If you'd like to scrape search history (or other
interesting history like youtube, location, voice, etc), better options would be 
using a headless browser like PhantomJS, or creating a chrome extension.  Since 
search history is synced across devices, you could get searches from mobile chrome.

__Update July 2016:__ Google has bundled all history items including voice, location,
YouTube, browser, search into myactivity.google.com.  This code won't work, but the approach
used here might.

