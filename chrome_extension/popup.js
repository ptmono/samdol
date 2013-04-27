var Var = {
    host: "127.0.0.1",
    port: "8559",
    // have to sync with server/config.Var.status
    status: {
	"000": "Reset to change!", 		//All OK
	"401": 'Url not supported', 		//NoContainerException
	"402": 'Maybe server is not work'       //ConnectionError
    }
};

var Info = { 
    url: "",
    rating: "", 
    memo: "" ,
    
    get: function(tab) {
	this.url = tab.url;
	
	this.rating = $("input:radio:checked").val();
	if (typeof this.rating == "undefined") rating = 0;

	this.memo = $(".comment").val();
	return this;
    }

};

function createUrl(req) {
    return "http://" + Var.host + ":" + Var.port + "/" + req;
}

function clickHandler(e) {

    chrome.tabs.getSelected(null, function(tab) {

	var myObj = Info.get(tab);
	var url = createUrl("post");// + JSON.stringify(myObj);
	$("#response").html("Parsing...");
	$.ajax({ type: "GET",
		 url: url,
		 // It seems data automatically escaped.
		 data: { url: tab.url,
			 rating: $("input:radio:checked").val(),
			 memo: $(".comment").val()
		       },

		 success: function (data) {
		     // Fixme: I have no idea why data contains None string.
		     var data_s = data.replace("None", "");
		     var msg = $.evalJSON(data_s).msg;
		     var status = $.evalJSON(data_s).status;

		     console.log($.evalJSON(data_s).msg);
		     $("#response").html(msg);
		 }

	       });
    });
}

////// submit problem
// 
// We couldn't use normal submit because "Content Security Policy".
// - http://developer.chrome.com/extensions/contentSecurityPolicy.html

// We couldn't use inline script. So we need this popup.js. To call a
// javascript function with submit of form tag, we can use onsumit
// attribute or javascript action in action attribute. For instance
// <form name="frm1" action="tryjsref_form_onsubmit.htm" onsubmit="greeting()">
// <form name="frm1" action="javascript:greeting()">

// But we can't use inline script by the content security policy. We can
// use addEventListener instead of inline script to execute a javascript
// with button.

// Other way that does not tested is to use jquery's submit.
// $(function(){
//     $("form").submit(function() {
// 	$("h1").html("bbbeeeeeeeeeeeeeeeeee");
// 	window.close();
//     });
// });

// Add event listeners once the DOM has fully loaded by listening for the
// `DOMContentLoaded` event on the document, and adding your listeners to
// specific elements when it triggers.
// document.addEventListener('DOMContentLoaded', function () {
//   document.querySelector('button').addEventListener('click', clickHandler);
// });
$(document).ready(function(){
    var url_calendar = createUrl("calendar");
    var url_recruits = createUrl("recruits");
    $('button[name=calendar]').bind('click', function() {
	chrome.tabs.create({url: url_calendar});
    });
    $('button[name=submit]').bind('click', clickHandler);

    $('button[name=permanent]').bind('click', function() {
	chrome.tabs.create({url: url_recruits});
    });
});



function redHtml(str){
    return '<b><font color="red">' + str + '<!/font></b>';
}

function initPopup(){
    chrome.tabs.getSelected(null, function(tab) {
	var url = "http://localhost:8559/get";
	var send_req = { url: tab.url };

	$.getJSON(url, send_req, function(data) {
	    console.log(data);

	    if (data.rating){
	    	$('input').rating('select', data.rating);
		$(".comment").val(data.memo);
		$("#response").html("On database");
	    }
	    else{
		$("#response").html(data.msg);
	    }

	    // TODO: how to get simply the length of json object.
	    // var key, count = 0;
	    // for (key in data)
	    // 	count++;
	    // if (count)
	    // 	$("#response").html("On database.");
	    // else
	    // 	$("#response").html("New recruit");

	});
	
    });
}


////// How to use jquery star plugin
//
// - http://www.fyneworks.com/jquery/star-rating/#tab-Testing
// popup.html shows the example.
// Just list input tag. If we click a star, then checked attribute is added.
// <input class="star" type="radio" name="test-2-rating-1" value="M" title="Maybe" checked="checked"/>
//
// To get the value to be rating, we can use "$("input:radio:checked").val().

// Init star
$(function(){
    $('.hover-star').rating({
	focus: function(value, link){
	    // 'this' is the hidden form element holding the current value
	    // 'value' is the value selected
	    // 'element' points to the link element that received the click.
	    var tip = $('#hover-test');
	    tip[0].data = tip[0].data || tip.html();
	    tip.html(link.title || 'value: '+value);
	},
	blur: function(value, link){
	    var tip = $('#hover-test');
	    $('#hover-test').html(tip[0].data || '');
	}
    });
});

$(function() {
    initPopup();
    //$(".comment").focus();
    setTimeout(function() {
	$('.comment').focus();
    }, 500);

});

