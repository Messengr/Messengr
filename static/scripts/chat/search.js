$(document).ready(function(){
    var symmetric_key;
    
    // Scroll to bottom
    $("#chat_base").scrollTop($("#chat_base")[0].scrollHeight);

    $('#returnToChat').click(function (url) {
        var new_path = window.location.href;
        new_path = new_path.substr(0, new_path.length - 7);
        window.location.href = new_path;
    });
    
    $(".text-warning").each(function(index, element) {
        if (!symmetric_key) {
            computeSymmetricKey();
        }
        var enc_message = $(this).text();
        var decrypted_msg = sjcl.decrypt(symmetric_key, enc_message);
        $(this).text(decrypted_msg);
    });

    function computeSymmetricKey() {
        var serialized_sk = JSON.parse(localStorage.getItem(CURRENT_USERNAME))["secret_key"];
        // Unserialized private key:
        var unserialized_sk = new sjcl.ecc.elGamal.secretKey(
            sjcl.ecc.curves.c256,
            sjcl.ecc.curves.c256.field.fromBits(sjcl.codec.base64.toBits(serialized_sk))
        );
        symmetric_key = sjcl.decrypt(unserialized_sk, ENCRYPTED_SYM_KEY);
    }
    
    /**
     * Checks if message has been processed before and processes if not.
     * @param {integer} message_id The identifier for a message.
     * @param {string} message The message to be processed.
     * @return {boolean} Returns a boolean of whether or not the message was processed.
     */
    function processNewMessage(message_id, message) {
        var message_key = "message-" + message_id.toString();
        var processed_id = JSON.parse(localStorage.getItem(CURRENT_USERNAME))[message_key];
        if (processed_id != null) {
            return false;
        } else {
            processMessage(symmetric_key, message_id, message, chat_id);
            var user_data = JSON.parse(localStorage.getItem(CURRENT_USERNAME));
            user_data[message_key] = "processed";
            localStorage.setItem(CURRENT_USERNAME, JSON.stringify(user_data));
        }
        return true;
    }
});