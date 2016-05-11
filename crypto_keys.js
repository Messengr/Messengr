var generateKeys = function() {
    var pair = sjcl.ecc.elGamal.generateKeys(256);
    console.log(pair);
    var par = document.createElement("p");
    var node = document.createTextNode(String(pair));
    par.appendChild(node);
    
    var element = document.getElementById("keys");
    element.appendChild(par);
};