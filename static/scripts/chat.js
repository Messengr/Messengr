// Useful format function
if (!String.format) {
  String.format = function(format) {
    var args = Array.prototype.slice.call(arguments, 1);
    return format.replace(/{(\d+)}/g, function(match, number) { 
      return typeof args[number] != 'undefined'
        ? args[number] 
        : match
      ;
    });
  };
}

$(document).ready(function(){
    // Scroll to bottom
    $("#chat_base").scrollTop($("#chat_base")[0].scrollHeight);

    var socket;
    var current_username;

    socket = io.connect('http://' + document.domain + ':' + location.port + '/chat');
    socket.on('connect', function() {
        socket.emit('joined', {});
    });
    socket.on('username', function(data) {
        // Cache current user's name
        current_username = data['username'];
    });
    // Status message when user enter/leaves chat
    socket.on('status', function(data) {
        alert(data['msg']);
    });
    // Display new message
    socket.on('message', function(data) {
        var msg = data['msg'];
        var sender = data['sender'];
        var receiver = data['receiver'];
        var dt = data['dt'];
        if (current_username == sender) {
            $("#chat_base").append(newSenderMessage(msg, sender, dt));
        }
        if (current_username == receiver) {
            $("#chat_base").append(newReceiverMessage(msg, sender, dt));
        }
        // Scroll to bottom
        $("#chat_base").scrollTop($("#chat_base")[0].scrollHeight);
    });

    // Click 'Send' button when 'Enter' key is pressed
    $("#message").keyup(function(event){
        if(event.keyCode == 13){
            $("#send_message").click();
        }
    });
    // Send new message to server when 'Send' button is clicked
    $("#send_message").click(function() {
        var message = $('#message').val();
        if (message === '') {
            // Empty message, do not send
            return;
        }
        // Clear message box
        $('#message').val('');
        // Send message to server
        socket.emit('new_message', {msg: message});
    });
    // Disconnect socket and go to home page when 'Leave Chat' button is clicked
    $('#leaveChat').click(function (url) {
        socket.emit('left', {}, function() {
            socket.disconnect();
            // Go back to the login page
            window.location.href = "/";
        });
    });

    function newSenderMessage(msg, username, dt) {
        var message = "<div class='row msg_container base_sent'>" + 
                    "<div class='col-md-10 col-xs-10'>" + 
                    "<div class='messages msg_sent'>" +
                    "<p class='text-warning'>{0}</p>" +
                    "<time datetime='{2}' class=''>{1} • {2}</time>" +
                    "</div>" + 
                    "</div>" +
                    "<div class='col-md-2 col-xs-2 avatar'>" +
                    "<img src='http://www.bitrebels.com/wp-content/uploads/2011/02/Original-Facebook-Geek-Profile-Avatar-1.jpg' height='100' width='100' class='img-responsive'>" +
                    "</div>" +
                    "</div>";
        return String.format(message, msg, username, dt);
    };

    function newReceiverMessage(msg, username, dt) {
        var message = "<div class='row msg_container base_receive'>" +
                "<div class='col-md-2 col-xs-2 avatar'>" +
                "<img src='http://www.bitrebels.com/wp-content/uploads/2011/02/Original-Facebook-Geek-Profile-Avatar-1.jpg' height='100' width='100' class='img-responsive'>" +
                "</div>" +
                "<div class='col-md-10 col-xs-10'>" +
                "<div class='messages msg_receive'>" +
                "<p class='text-warning'>{0}</p>" +
                "<time datetime='{2}' class=''>{1} • {2}</time>" +
                "</div>" +
                "</div>" +
                "</div>";
        return String.format(message, msg, username, dt);
    };
});