$(document).ready(function(){

    $('#create_account').submit(function(e) {
        // Stop form from submitting
        e.preventDefault();

        var pair = sjcl.ecc.elGamal.generateKeys(256);
        var pub = pair.pub.get(), sec = pair.sec.get();

        // Serialized public key:
        var pub_serialized = sjcl.codec.base64.fromBits(pub.x.concat(pub.y));

        // Serialized private key:
        var sec_serialized = sjcl.codec.base64.fromBits(sec);

        // Get all inputs
        var req_data = {"public_key": pub_serialized};
        $.each($('#create_account').serializeArray(), function(i, field) {
            req_data[field.name] = field.value;
        });

        // Safety checks
        var error;
        var username = req_data['username'];
        var password = req_data['password'];
        if (!username || !password) {
            error = "Request missing a field!";
        }
        if (username.length === 0 || username.length > 32) {
            error = "Invalid username. Must be nonempty and contain at most 32 characters.";
        }
        if (username.match(/^[a-zA-Z0-9_-]+$/) == null || username.match(/^[a-zA-Z0-9_-]+$/)[0] !== username) {
            error = "Invalid username. Must contain only letters (a-z), numbers (0-9), dashes (-), underscores (_).";
        }
        if (password.length < 8 || password.length > 128) {
            error = "Invalid password. Must be at least 8 characters and at most 128 characters.";
        }
        if (error) {
            $('#create_account')[0].reset();
            alert(error);
            return false;
        }

        // Try to create account
        $.post($SCRIPT_ROOT + '/user/create', req_data, function(data) {
            if (data.error) {
                $('#create_account')[0].reset();
                alert(data.error);
                return;
            }
            if (!data.username) {
                $('#create_account')[0].reset();
                alert("Unexpected error. Please try again later.");
                return;
            }
            // Account successfully created
            // Store keys in local storage
            var username = data.username;
            var public_key_name = username + "_public_key";
            var secret_key_name = username + "_secret_key";
            localStorage.setItem(public_key_name, pub_serialized);
            localStorage.setItem(secret_key_name, sec_serialized);
            // Redirect to homepage
            window.location.href = $SCRIPT_ROOT + "/";
        });
    });

});
