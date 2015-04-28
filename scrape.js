var fs = require('fs');
var system = require('system');
require("config.js");
var links = [];
var casper = require('casper').create({
    verbose: true,
    pageSettings: {
	    userAgent: 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:37.0) Gecko/20100101 Firefox/37.0'
    },
    viewportSize: {
        width: 1024,
        height: 768
    },
});



function append(mess){
    if(mess == mostRecent){
          reachedPriorSearch = true; 
    }
    if(!reachedPriorSearch && n < maxN){
      system.stdout.write(mess + "\n");
      fs.write('to_tweet.txt', mess + "\n", "a+");
      n++;
      if(!foundMostRecent){
          foundMostRecent = true;
          fs.write('most_recent.txt', mess+"\n", 'w');
      }
    }
}

var snaps=0;
function snap(cap){
    cap.capture('google_'+snaps+'.png', {
        top: 0,
        left: 0,
        width: 1024,
        height: 768
    });
    snaps++;
}

casper.start('https://history.google.com/history', function() {
    snap(this);
});

casper.on('remote.message', function(msg) {
    append(msg);
})

casper.then(function() {
   //this.mouse.click(400, 300);
   this.sendKeys('input[name="Email"]', config.google_username);
   this.sendKeys('input[name="Passwd"]',config.google_password);
   this.click('input[name="signIn"]');
});

var mostRecent = null;
var maxN = 30; // sanity check to never get more than 30 searches
data = fs.read("most_recent.txt");
data = data.split("\n")
if (!data || data.length < 1 || data[0] == "") {
    mostRecent = null;
    maxN = 1;
} else {
    mostRecent = data[0]
}
var n = 0;
var reachedPriorSearch = false;
var foundMostRecent = false;

fs.write('to_tweet.txt', "", "w");

casper.then(function(){
        this.evaluate(function(){
            for(var i=0; i<36; i++){
                var tab = document.getElementById('r'+i);
                if(tab){
                    var ah = tab.getElementsByTagName("a")[0];
                    console.log(ah.innerHTML);
                 }
            }
        });
        this.mouse.click(968, 402);
});

casper.run(function() {
    this.exit();
});
