$(document).ready(function(){
    // Redirect to corresponding chat when clicking on table row
    $('tr').click(function() {
        if (this.id !== "") {
            window.location.href = '/chat/' + this.id;
        }
    });    

    // Click 'New Chat' button when 'Enter' key is pressed
    $("#receiver").keyup(function(event){
        if(event.keyCode == 13){
            $("#new_chat").click();
        }
    });

    // Try to create new chat when 'New Chat' button is clicked
    $("#new_chat").click(function() {
        var receiver_username = $('#receiver').val();
        // Clear message box
        $('#receiver').val('');
        if (receiver_username === '' || receiver_username.length > 16) {
            // Invalid username, do not send
            return;
        }
        $.getJSON($SCRIPT_ROOT + '/public_key', {
            'receiver_username': receiver_username
        }, function(data) {
            if (data.error) {
                alert(data.error);
                return;
            }
            // Get public keys
            var my_public_key = data.sender_public_key;
            var receiver_public_key = data.receiver_public_key;

            // TODO: Generate secret symmetric key
            var secret_sym_key = "blah";
            // Encrypt it using my public key
            var sk_sym_1 = sjcl.encrypt(my_public_key, secret_sym_key);
            // Encrypt it using receiver's public key
            var sk_sym_2 = sjcl.encrypt(receiver_public_key, secret_sym_key);
            // Send both encrypted keys to server
            var req_data = {
                'sk_sym_1': sk_sym_1,
                'sk_sym_2': sk_sym_2,
                'receiver_username': receiver_username,
                'receiver_public_key': receiver_public_key
            };
            $.post($SCRIPT_ROOT + '/chat/create', req_data, function(data) {
                if (data.error) {
                    alert(data.error);
                    return;
                }
                chat_id = data.chat_id;
                window.location.href = $SCRIPT_ROOT + "/chat/" + chat_id;
            });
        });
    });

});
