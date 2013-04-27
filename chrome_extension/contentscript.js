// in the content script, listen for Crtl+Shift+E (upper or lowercase)
document.documentElement.addEventListener("keypress", function(e) {
    if((e.keyCode == 69 || e.keyCode == 101) && e.ctrlKey && e.shiftKey) {
        // do something (step 2, below)
	window.alert("sometext");
	console.log("aaaa");
    }
}, true);
