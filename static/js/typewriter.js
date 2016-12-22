// created type writer effect by using typed.js

setTimeout(function(){
    $("#welcome-phrase").typed({
        strings: ["Welcome to Full Circle Travel Blog", "Dedicated to helping you share your stories", "Login or signup to get started"],
        typeSpeed: 30, // typing speed
        backDelay: 750, // pause before backspacing
        loop: false, // loop on or off (true or false)
        loopCount: false, // number of loops, false = infinite
        callback: function(){ } // call function after typing is done
    });
}, 0);