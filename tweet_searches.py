from scrape_history import get_history
import twitter
import argparse
import time

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Search tweeter")
    parser.add_argument("username", help="Google username")
    parser.add_argument("password", help="Google password")
    parser.add_argument("--code", help="Google second factor auth code")
    parser.add_argument("--state_file", help="file storing most recent tweet (older searches ignored")
    parser.add_argument("--consumer_key")
    parser.add_argument("--consumer_secret")
    parser.add_argument("--access_token_key")
    parser.add_argument("--access_token_secret")

    args = parser.parse_args()

    outfile = args.state_file

    if args.consumer_key and args.consumer_secret and args.access_token_key and args.access_token_secret:
	api = twitter.Api(consumer_key=args.consumer_key,
			  consumer_secret=args.consumer_secret,
			  access_token_key=args.access_token_key,
			  access_token_secret=args.access_token_secret,
			  input_encoding="utf-8")
    else:
        print "Must supply twitter api credentials."

    history = get_history(args.username, args.password, args.code)
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
	try:
	    message.decode("utf-8")
            api.PostUpdate(message)
	except twitter.error.TwitterError as e:
	    print e
	except UnicodeDecodeError as e:
	    print e
        time.sleep(5)

    with open(outfile, 'w') as f:
	f.write(new_most_recent)
