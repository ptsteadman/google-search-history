var Twitter = require('twitter');
var exec = require("child_process").exec;
require("./config.js")

var client = new Twitter({
    consumer_key: config.consumer_key,
    consumer_secret: config.consumer_secret,
    access_token_key: config.access_token_key,
    access_token_secret: config.access_token_secret
});

function tweetTweets(tweets, i){
    if (i < 0 || tweets.length == 0) return;
    if(tweets[i] && tweets[i] != ""){
	   console.log("sending tweet:" + tweets[i]);
	client.post('statuses/update', {status: tweets[i]},  function(error, tweet, response){
	    if(error) throw error;
	    console.log(tweet);  // Tweet body. 
            tweetTweets(tweets.slice(0,i), i - 1);
	});
    } else {
            tweetTweets(tweets.slice(0,i), i - 1);
	  }
}

function getTweets(){
    exec("/usr/local/bin/casperjs /home/ubuntu/theosearch/scrape.js", function(err, stdout, stderr){
	if(stdout){
	    tweets = stdout.split("\n");
	    if(tweets && tweets.length > 0){
		    console.log("method called");
		tweetTweets(tweets, tweets.length - 1)
	    }
	}
	if(stderr) console.log("error" + stderr);
	if (err !== null) {
	    console.log('exec error: ' + error);
	}
    });
}

getTweets();
