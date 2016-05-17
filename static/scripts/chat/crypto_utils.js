// Crypto Utils
// Implements:
// - sha256
// - hmac256
// - tokenizer for secret key and keyword
// - Hex xor calculator
// - Hex xor calculator for id
// - entryEncoder 
// - complete message entry encoder

/**
 * Applies the SHA256 hash on a message.
 * @param {string} message A string that represents the message to hash.
 * @return {string} The hashed form of the message.
 */
function sha256(message) {
    var bitArray = sjcl.hash.sha256.hash(message);
    var digest_sha256 = sjcl.codec.hex.fromBits(bitArray);
    return digest_sha256;
}

/**
 * Takes in a key and a message to process. Uses SHA256 to process the key/message pair.
 * @param {string} key utf8String used as the secret for the hmac.
 * @param {string} message The message to be processed.
 * @return {string} Hashed value of information.
 */
function hmac256(key, message) {
    var secret = sjcl.codec.utf8String.toBits(key);
    var hmac = new sjcl.misc.hmac(secret, sjcl.hash.sha256);
    hmac.update(sjcl.codec.utf8String.toBits(message));
    return sjcl.codec.hex.fromBits(hmac.digest());
}

/**
 * Generates a token given a key and a keyword.
 * @param {string} key The user's secret key.
 * @param {string} keyword The keyword to query.
 * @return {string} returns The result of running hmac-sha256 on our key and sha256 of our keyword.
 */
function tokenize(key, w) {
    return hmac256(key, sha256(w));
}


/**
 * Calculates the xor value of two hex strings of equal length.
 * @param {string} left The left value in the xor operation.
 * @param {string} right The right value in the xor operation.
 * @returns {string} The output of the xor of our two hex strings.
 */
function xorHex(left, right) {
    if (left.length != right.length) {
        throw new Error("Invalid arguments for xorHex function. Received arguments of length " + left.length + " and " + right.length + ". Expected equal length inputs.");
    }
    var result = "", temp;
    for (i = 0; i < left.length; i++) {
        temp = parseInt(left.charAt(i), 16) ^ parseInt(right.charAt(i), 16);
        result += (temp).toString(16);
    }
    return result;
}

/**
 * Calculates the xor of a message identifier (16 chars) with our computed hash value (64 chars long).
 * @param {string} id The message identifier of a message. It should be 16 characters long.
 * @param {string} hmacResult The result of calculating hmac256(token, count + "1") for a given integer value, count.
 * @return {string} Returns the xor of the inputs.
 */
function xorWithId(id, hmacResult) {
    // id is always 16 characters long, the head never changes
    var head = hmacResult.substring(0, 48);
    var tail = hmacResult.substring(48, 64);
    var newTail = xorHex(id, tail);
    return head + newTail;
}

/**
 * Produces an encoded key value pair (hkey, c1) in the javascript object format from the
 * secret key, the keyword, document id and the current count (how many times this keyword has shown up).
 * @param {string} key The key for the symmetric encryption used.
 * @param {string} w The keyword for this entry.
 * @param {integer} id The document id for this entry.
 * @param {integer} cnt The count of this entry.
 * @return {object} Returns a javascript object containing the hash key and hash value (key/value pair for hash).
 */
function encodeEntry(key, w, id, cnt) {
    var token = tokenize(key, w);
    var hkey = hmac256(token, cnt + "0"); // Hash Key = HMAC(k, cnt || "0")
    id = id.toString(16); // rewrite in hex format
    var c1 = xorWithId(id, hmac256(token, cnt + "1")); // Hash Value = id ^ HMAC(k, cnt || "1")
    return {
        "hkey": hkey,
        "hval": c1
    };
}

/**
 * Produces the encoded pairs from a message.
 * @param {string} key The secret key for our search protocol.
 * @param {string} id The message identifier of the current message being processed.
 * @param {string} message Plaintext message to be processed.
 * @return {list} Returns a list of encoded pairs to store in our online database.
 */
function produceEncodedPairList(key, id, message) {
    var keywordList = getKeywords(message);
    var encodedPairList = [];

    keywordList.forEach(function (keyword, index, array) {
        var safeKeyword = "keyword-" + keyword;
        var keyword_count = localStorage.getItem(safeKeyword);
        
        if (keyword_count == null) {
            keyword_count = 1;
        } else {
            keyword_count = parseInt(keyword_count)+1;
        }
        localStorage.setItem(safeKeyword, keyword_count);
        
        // Update document count for keyword.
        var encodedPair = encodeEntry(key, keyword, id, keyword_count);
        encodedPairList.push(encodedPair);
    });

    return encodedPairList;
}