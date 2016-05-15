$(document).ready(function() {

    // Attach '.active' to current page's link in navbar
    $("ul.nav li").each(function(i, e) {
        var path = $(e).find('a').attr('href');
        if(path === window.location.pathname) {
            $(e).addClass("active");
        }
    });
    
    // Load javascript crypto library
//    var url = "/static/scripts/sjcl.js";
//    $.getScript( url, function() {
//                
//        $('#create_account').submit(function(eventObj) {
//            var pair = sjcl.ecc.elGamal.generateKeys(256);
//            var pub = pair.pub.get(), sec = pair.sec.get();
//
//            // Serialized public key:
//            var pub_serialized = sjcl.codec.base64.fromBits(pub.x.concat(pub.y));
//
//            // Serialized private key:
//            var sec_serialized = sjcl.codec.base64.fromBits(sec);
//
//            localStorage.setItem("public_key", pub_serialized);
//            localStorage.setItem("secret_key", sec_serialized); 
//
//            $(this).append('<input type="hidden" name="public_key" value="' + pub_serialized + '" /> ');
//            return true;
//        });
//        
//        $('#send_message').click(function(eventObj) {
//            // Initialize encryption keys
//            var recepient_pk_serialized = $('#receiver_pk').text();
//            var sk_serialized = localStorage.getItem("secret_key");
//            var symmetric_key = "abc"; // TODO: Replace with actual symmetric key.
//
//            if (sk_serialized == null || recepient_pk_serialized == null || symmetric_key == null) {
//                console.log("Issue retrieving keys.");
//                return false;
//            }
//            
//            var recepient_pk = new sjcl.ecc.elGamal.publicKey(
//                sjcl.ecc.curves.c256,
//                sjcl.ecc.curves.c256.field.fromBits(sjcl.codec.base64.toBits(recepient_pk_serialized))
//            );
//            
//            var message = $('#message').val();
//            console.log(message);
//            var encrypted_message = sjcl.encrypt(symmetric_key, message);
//            $('#message').val(encrypted_message);
//            console.log(encrypted_message);
//            return true;
//        });
//        
//        $(".text-warning").each(function(index, element) {
//            var symmetric_key = "abc"; // TODO: Replace with actual symmetric key.
//            var enc_message = $(this).text();
//            var pt = sjcl.decrypt(symmetric_key, enc_message);
//            $(this).text = pt;
//        });
//        
//    });

    // Redirect to corresponding chat when clicking on table row
    $('tr').click(function() {
        if (this.id !== "") {
            window.location.href = '/chat/' + this.id;
        }
    });    

});

