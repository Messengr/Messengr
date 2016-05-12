$(document).ready(function() {

    // Attach '.active' to current page's link in navbar
    $("ul.nav li").each(function(i, e) {
        var path = $(e).find('a').attr('href');
        if(path === window.location.pathname) {
            $(e).addClass("active");
        }
    });
    
    var url = "/static/scripts/sjcl.js";
    $.getScript( url, function() {
        $('#create_account').submit(function(eventObj) {
            console.log("called");
            var pair = sjcl.ecc.elGamal.generateKeys(256);
            var pub = pair.pub.get(), sec = pair.sec.get();

            // Serialized public key:
            var pub_serialized = sjcl.codec.base64.fromBits(pub.x.concat(pub.y));

            // Serialized private key:
            var sec_serialized = sjcl.codec.base64.fromBits(sec);

            localStorage.setItem("public_key", pub_serialized);
            localStorage.setItem("secret_key", sec_serialized); 

            $(this).append('<input type="hidden" name="public_key" value="' + pub_serialized + '" /> ');
            return true;
        });
    });
    
});


