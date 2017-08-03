/*******************************************************************************
Argon Design Ltd. Project P9000 Argon
(c) Copyright 2017 Argon Design Ltd. All rights reserved.

Module : maybot
Author : Steve Barlow
$Id: speak.js 18332 2017-06-18 16:18:38Z sjb $

DESCRIPTION:
JavaScript to speak text in an approximation of Theresa May's voice
*******************************************************************************/

// See https://developers.google.com/web/updates/2014/01/Web-apps-that-talk-Introduction-to-the-Speech-Synthesis-API
// Fix for long text from https://bugs.chromium.org/p/chromium/issues/detail?id=335907 comment 34

function speak(text) {
    if ('speechSynthesis' in window) {
        speechSynthesis.cancel();

        var msg = new SpeechSynthesisUtterance();
        msg.volume = 1;  // 0 to 1
        msg.rate = 0.77; // 0.1 to 10
        msg.pitch = 0.9; // 0 to 2
        msg.text = text;
        msg.lang = 'en-GB';
        
        // Not using 'msg.voice =' as it is ignored on Android
        // On Android can only get an American accent

        var timer;
        msg.addEventListener('end', function() {
            clearTimeout(timer);
        });

        //IMPORTANT!! Do not remove: Logging the object out fixes some onend firing issues
        console.log(msg);
        // Placing the speak invocation inside a callback fixes ordering and onend issues
        setTimeout(() => {
            speechSynthesis.speak(msg);
        }, 0);

        timer = setTimeout(function pauseResumeTimer() {
            speechSynthesis.pause();
            //IMPORTANT!! Do not remove: Logging the object out fixes some onend firing issues
            console.log(msg);
            // Placing the speak invocation inside a callback fixes ordering and onend issues
            setTimeout(() => {
                speechSynthesis.resume();
            }, 0);
            timer = setTimeout(pauseResumeTimer, 10000)
        }, 10000);
    }
}
