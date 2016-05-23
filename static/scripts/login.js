$(document).ready(function(){

    function sha256(text) {
        var bitArray = sjcl.hash.sha256.hash(text);
        var digest_sha256 = sjcl.codec.hex.fromBits(bitArray);
        return digest_sha256;
    }

    $('#login').submit(function(e) {
        // Stop form from submitting
        e.preventDefault();

        // Get all inputs
        var req_data = {};
        $.each($('#login').serializeArray(), function(i, field) {
            req_data[field.name] = field.value;
        });

        // Send SHA256 of password
        var password = req_data['password'];
        req_data['password'] = sha256(password);

        $.post($SCRIPT_ROOT + '/login', req_data, function(data) {
            if (data.error) {
                $('#login')[0].reset();
                alert(data.error);
                return;
            }
            if (!data.user_data) {
                $('#login')[0].reset();
                alert("Unexpected error. Please try again later.");
                return;
            }
            // Successfully logged in
            // Decrypt user-data and store
            var encrypted_user_data = data.user_data;
            var user_data = sjcl.decrypt(password, encrypted_user_data);
            sessionStorage.setItem(req_data['username'], user_data);
            // Redirect to homepage
            window.location.href = $SCRIPT_ROOT + "/";
        });
    });

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
        if (!password.match(/^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}$/)) {
            error = "Invalid password. Must be at least 8 characters and contain a lowercase letter, an uppercase letter, and a digit.";
        }
        if (error) {
            $('#create_account')[0].reset();
            alert(error);
            return false;
        }

        req_data['password'] = sha256(password);

        var user_data = {'username': username, 'public_key': pub_serialized, 'secret_key': sec_serialized};
        var encrypted_user_data = sjcl.encrypt(password, JSON.stringify(user_data));
        req_data['user_data'] = encrypted_user_data;

        // Try to create account
        $.post($SCRIPT_ROOT + '/user/create', req_data, function(data) {
            if (data.error) {
                $('#create_account')[0].reset();
                alert(data.error);
                return;
            }
            // Account successfully created
            // Store user-data
            sessionStorage.setItem(username, JSON.stringify(user_data));
            // Redirect to homepage
            window.location.href = $SCRIPT_ROOT + "/";
        });
    });

});
