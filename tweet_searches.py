import 
if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Search tweeter")
    parser.add_argument("username", help="Google username")
    parser.add_argument("password", help="Google password")
    parser.add_argument("--code", help="Google second factor auth code")
    parser.add_argument("--tweet", help="actually tweet the most recent searches",
                        action="store_true")
    parser.add_argument("--file", help="file storing most recent tweet (older searches ignored")
    parser.add_argument("--consumer_key", help="file storing most recent tweet (older searches ignored")
    parser.add_argument("--file", help="file storing most recent tweet (older searches ignored")
    parser.add_argument("--file", help="file storing most recent tweet (older searches ignored")
    parser.add_argument("--file", help="file storing most recent tweet (older searches ignored")


    
    argc = len(sys.argv)
    if argc < 5 or argc > 6:
        sys.exit('Usage: python search_tweeter.py tweet statefile email passwd [code]')

    tweet_new = sys.argv[1]
    outfile = sys.argv[2]
    email = sys.argv[3]
    passwd = sys.argv[4]
    code = None
    if argc == 6:
        code = sys.argv[5]

    if tweet_new:
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
	if tweet_new:
        api.PostUpdate(message)
	    time.sleep(5)

    with open(outfile, 'w') as f:
	f.write(new_most_recent)
