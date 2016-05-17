// Message Utils
// Implements:
// - Message keyword extraction

/**
 * Remove duplicates from an array. From http://dreaminginjavascript.wordpress.com/2008/08/22/eliminating-duplicates/
 */
function eliminateDuplicates(arr) {
    var i,
        len = arr.length,
        out = [],
        obj = {};

    for (i = 0; i < len; i++) {
        obj["keyword-" + arr[i]] = 0;
    }
    for (i in obj) {
        var strLength = i.length;
        var originalKeyword = i.substring(8); // trim off first 8 chars "keyword-"
        out.push(originalKeyword);
    }
    return out;
}

/**
 * Extracts the unique keywords from a string.
 * @param {string} message The text from which we are extracting keywords.
 * @return {list} The list of unique words from our input.
 */
function getKeywords(message) {
    text = message.match(/(w+)/g);
    var allowedChars = /[^a-zA-Z']+/g;
    // Remove all irrelevant characters
    text = message.replace(allowedChars, " ").replace(/^\s+/, "").replace(/\s+$/, "");
    text = text.toLowerCase();
    wordList = text.split(/\s+/);
    wordList = eliminateDuplicates(wordList);
    return wordList;
}