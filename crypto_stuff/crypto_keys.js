var pub_serialized = "";
var sec_serialized = "";

var generateKeys = function() {
    var pair = sjcl.ecc.elGamal.generateKeys(256);
    var pub = pair.pub.get(), sec = pair.sec.get();

    // Serialized public key:
    var pub_serialized = sjcl.codec.base64.fromBits(pub.x.concat(pub.y));
    
    // Serialized private key:
    var sec_serialized = sjcl.codec.base64.fromBits(sec);
    
    window.pub_serialized = pub_serialized;
    window.sec_serialized = sec_serialized;
    
    document.getElementById("pk").textContent = pub_serialized;
    document.getElementById("sk").textContent = sec_serialized;
};

var testECC = function () {
    if (window.pub_serialized == "" || window.sec_serialized == ""){
        alert("Must generate key first!");
        return;
    } else {
        var pub = new sjcl.ecc.elGamal.publicKey(
                      sjcl.ecc.curves.c256, 
                      sjcl.codec.base64.toBits(window.pub_serialized)
                  );
        var sec = new sjcl.ecc.elGamal.secretKey(
                      sjcl.ecc.curves.c256,
                      sjcl.ecc.curves.c256.field.fromBits(sjcl.codec.base64.toBits(window.sec_serialized))
                  );
    }

    var message = document.getElementById("message").value;
    var ct = sjcl.encrypt(pub, message);
    var pt = sjcl.decrypt(sec, ct);
    
    document.getElementById("ciphertext").value = ct;
    document.getElementById("plaintext").value = pt;
    console.log(message);
    console.log(ct);
    console.log(pt);
}
