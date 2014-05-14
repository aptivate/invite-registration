django.jQuery(function ($) {
    function onSuccess(data, textStatus, jqXHR) {
        var msg = "Invitation was successfully sent.";
        alert(msg);
    }

    function onError(jqXHR, testStatus, errorThrown) {
        var msg = "There was an error. Please try again later\n" +
                  "\nReported error: " + errorThrown;
        alert(msg);
    }

    function sendInvitation(e) {
        var activation_url = $('#send-activation-url').val(),
            csrf_token = $('[name="csrfmiddlewaretoken"]').val();
        $.ajax({
            type: "GET",
            url: activation_url,
            headers: { 'X-CSRFToken': csrf_token },
            data: { hide_messages: 1 }
        }).done(onSuccess)
          .error(onError);

        e.stopPropagation(); e.preventDefault();
    }

    $("<a>", {
        href:"#",
        text:"Send invitation"
    }).css({
        marginRight: "20px"
    }).on("click", sendInvitation
    ).prependTo(".submit-row");
});
