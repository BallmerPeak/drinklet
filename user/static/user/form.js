var csrftoken = $.cookie('csrftoken');

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
function sameOrigin(url) {
    // test that a given url is a same-origin URL
    // url could be relative or scheme relative or absolute
    var host = document.location.host; // host + port
    var protocol = document.location.protocol;
    var sr_origin = '//' + host;
    var origin = protocol + sr_origin;
    // Allow absolute or scheme relative URLs to same origin
    return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
        (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
        // or any other URL that isn't scheme relative or absolute i.e relative.
        !(/^(\/\/|http:|https:).*/.test(url));
}
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
            // Send the token to same-origin, relative URLs only.
            // Send the token only if the method warrants CSRF protection
            // Using the CSRFToken value acquired earlier
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

var user = function () {
    var login, jqxhr;

    login = function (username, password) {
        jqxhr = $.post('/user/login',
            {
                'username': username,
                'password': password
            });

        return jqxhr;
    };

    return {
        'login': login
    };
}();


$(document).ready(function(){
    var username, password, loginModalContent, replaceHtml;
	// Open the modal


	$('.nav-wrapper .modal-trigger').leanModal({
        ready: function() {
            $('#loginUsername, #regUsername').focus();
        },
		// Modal complete event handler
		complete: function() { 
			// Remove all overlays
		 }	
	});

    $('#loginModal').keypress(function (evt) {
        if(evt.which == 13) {
            $('button#login_button').click();
        }
    });

    $('#login_button').click(function() {
        username = $('#loginUsername').val().toLowerCase();
        password = $('#loginPassword').val();
        user.login(username, password)
            .done(function (data) {
                var jsonData = JSON.parse(data);
                if(jsonData.redirect)
                    window.location.href = jsonData.redirect;
            })
            .fail(function (data) {
                loginModalContent = $('#loginModal').find('> .modal-content');
                replaceHtml = $(data.responseText).find('.modal-content').html();
                loginModalContent.html(replaceHtml);
                $('#loginUsername').focus().select();
            })
        });

     $('#regBut').click(function() {
        username = $('#regUsername').val().toLowerCase();
        pwd1 = $('#regPassword').val();
        pwd2 = $('#regConfirmPassword').val();
        email = $('#regEmail').val();

        $.post('user/register', {'username':username,'pwd':pwd1,'pwd2':pwd2,'email':email})
            .done(function (data) {
                var jsonData = JSON.parse(data);
                if(jsonData.redirect)
                    window.location.href = jsonData.redirect;
            })
            .fail(function (data) {
                registerModalContent = $('#registerModal > .modal-content');
                replaceHtml = $(data.responseText).find('.modal-content').html();
                registerModalContent.html(replaceHtml);
            })
        });



});