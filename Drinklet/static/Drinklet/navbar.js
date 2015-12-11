$(document).ready(function() {
	// Allow for the navbar to turn into a side nav on mobile
	$(".button-collapse").sideNav({
		closeOnClick: true
	});

    if ($('#is-logged-in').length) {
        notifications.startNotifications();
    }
});

var notifications = (function() {
    var getNotifications, clear, startNotifications, stopNotifications,  stop = false;

    startNotifications = function () {
        clear = setTimeout(function () {
            if(stop) clearTimeout(clear);
            if(!$('#is-logged-in').length) clearTimeout(clear);

            getNotifications()
                .done(function (data) {
                    var $notificationContent, mobile, standard;
                    $notificationContent = $(data);
                    mobile = $notificationContent.find('#notification-mobile-wrapper').html();
                    standard = $notificationContent.find('#notification-wrapper').html();

                    $('#notification-mobile-wrapper').html(mobile);
                    $('#notification-wrapper').html(standard);

                    $('.collapsible').collapsible();
                    $('.dropdown-button').dropdown();
                });
            startNotifications();
        }, 30000);
    };

    getNotifications = function () {
        return $.get('/notifications/');
    };

    stopNotifications = function () {
        stop = true;
    };

    return {
        'startNotifications': startNotifications,
        'stopNotifications': stopNotifications
    };
}());