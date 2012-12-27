// A generic onclick callback function.
function genericOnClick(info, tab) {
    chrome.tabs.executeScript(tab.id, {file: ['inject.js', 'tools/jquery-1.8.3.min.js', 'tools/jquery.bpopup-0.7.0.min.js']}, function() {
	console.log('Successfully injected script into the page');
    });

    // chrome.tabs.sendRequest(tab.id, {method: "ping"}, function(response) {
    // 	console.log(response.data);
    // });

    // $('element_to_pop_up').bPopup({
    //     contentContainer:'.content',
    //     loadUrl: 'popup.html' //Uses jQuery.load()
    // });
                  

    var url = "http://localhost:8559/post";// + JSON.stringify(myObj);
    $.ajax({ type: "GET",
    	     url: url,
    	     // It seems data automatically escaped.
    	     data: { url: tab.url,
    		     rating: $("input:radio:checked").val(),
    		     memo: $(".comment").val()
    		   }
    	   });
}

var context_json = {"title": "Save this recruit",
		    "onclick": genericOnClick
		   };

chrome.contextMenus.create(context_json);
