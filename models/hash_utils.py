import hmac
import hashlib
import base64

def hmac256(key, message):
    return hmac.new(key, msg=message, digestmod=hashlib.sha256).hexdigest()
    
def xor_strings(hex_string_a, hex_string_b):
    binary_a = hex_string_a.decode("hex")
    binary_b = hex_string_b.decode("hex")
    return "".join(chr(ord(x) ^ ord(y)) for x, y in zip(binary_a, binary_b))
    
def get_id(hash_value, hash_decoupler):
    byte_hex_id = xor_strings(hash_value, hash_decoupler)[-8:] # Only need 8 bytes (2**64) for id
    id = 0
    for byte in byte_hex_id:
        id = (id * 256) + ord(byte)
    return id