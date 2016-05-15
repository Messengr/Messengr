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
    var testEncryption = true;
    
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
        
        if (testEncryption) {
            console.log("Received: ");
            console.log(msg);
            encrypted_msg = JSON.parse(msg);
            encrypted_msg.v = 1;
            encrypted_msg.iter = 1000;
            encrypted_msg.ks = 128;
            encrypted_msg.ts = 64;
            encrypted_msg.mode = "ccm";
            encrypted_msg.adata = "";
            encrypted_msg.cipher = "aes";
            console.log(encrypted_msg);
            decrypted_msg = sjcl.decrypt("abc", encrypted_msg);
            msg = decrypted_msg;
        }

        
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
        if (message.length > 128) {
            // Message must be at most 128 characters
            // Clear message box
            $('#message').val('');
            return;
        }
        
        // Initialize encryption keys
//        var recepient_pk_serialized = $('#receiver_pk').text();
//        var sk_serialized = localStorage.getItem("secret_key");
//        var symmetric_key = "abc"; // TODO: Replace with actual symmetric key.
//
//        if (sk_serialized == null || recepient_pk_serialized == null || symmetric_key == null) {
//            console.log("Issue retrieving keys.");
//        } else {
//
//            var recepient_pk = new sjcl.ecc.elGamal.publicKey(
//                sjcl.ecc.curves.c256,
//                sjcl.ecc.curves.c256.field.fromBits(sjcl.codec.base64.toBits(recepient_pk_serialized))
//            );
//
//            var encrypted_message = sjcl.encrypt(symmetric_key, message);
//            message = JSON.stringify(encrypted_message);
//            console.log(message);
//        }
        if (testEncryption) {
            var enc_message = sjcl.encrypt("abc", message);
            var enc_object = JSON.parse(enc_message);
            console.log(enc_object);
            var new_object = {"iv":enc_object.iv, "salt":enc_object.salt, "ct":enc_object.ct};
            message = JSON.stringify(new_object);
            
            encrypted_msg.v = 1;
            encrypted_msg.iter = 1000;
            encrypted_msg.ks = 128;
            encrypted_msg.ts = 64;
            encrypted_msg.mode = "ccm";
            encrypted_msg.adata = "";
            encrypted_msg.cipher = "aes";
            console.log(message);            
        }
        // Clear message box
        $('#message').val('');
        // Send message to server
        console.log("Message sent:");
        console.log(message);
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

    // TODO: Tony Crypto stuff...
    $(".text-warning").each(function(index, element) {
        var symmetric_key = "abc"; // TODO: Replace with actual symmetric key.
        var enc_message = JSON.parse($(this).text());
        var pt = sjcl.decrypt(symmetric_key, enc_message);
        $(this).text = pt;
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
                    "<img src='https://secure.gravatar.com/avatar/00000000000000000000000000000000?d=retro' height='100' width='100' class='img-responsive'>" +
                    "</div>" +
                    "</div>";
        return String.format(message, msg, username, dt);
    };

    function newReceiverMessage(msg, username, dt) {
        var message = "<div class='row msg_container base_receive'>" +
                "<div class='col-md-2 col-xs-2 avatar'>" +
                "<img src='https://secure.gravatar.com/avatar/00000000000000000000000000000000?d=retro' height='100' width='100' class='img-responsive'>" +
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