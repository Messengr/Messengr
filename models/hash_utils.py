import hmac
import hashlib
import base64

def hmac256(key, message):
    return hmac.new(key, msg=message, digestmod=hashlib.sha256).hexdigest()
    
def xor_strings(hex_string_a, hex_string_b):
    binary_a = hex_string_a.decode("hex")
    binary_b = hex_string_b.decode("hex")
    return "".join(chr(ord(x) ^ ord(y)) for x, y in zip(binary_a, binary_b))
    