from app import DB
from datetime import datetime
import hash_utils

column_length = 64

class EncodedPair(DB.Model):
    __tablename__ = 'encoded_pairs'

    id = DB.Column(DB.Integer, primary_key=True)
    hash_key = DB.Column(DB.String(column_length))
    hash_value = DB.Column(DB.String(column_length))
    
    def __init__(self, hash_key, hash_value):
        self.hash_key = hash_key
        self.hash_value = hash_value
        
    def __repr__(self):
        return '<Encoded Pair %r -> %r>' % (self.hash_key, self.hash_value)

    def to_dict(self):
        return {
            'id': self.id,
            'hash_key': self.hash_key,
            'hash_value': self.hash_value
        }


def insert_pairs(encoded_pairs):
    if len(encoded_pairs) == 0:
        return 0
    first_pair = encoded_pairs[0]
    check = EncodedPair.query.filter_by(hash_key=first_pair["hash_key"]).first()
    if check is not None:
        return 0
    
    db_pairs = []

    for encoded_pair in encoded_pairs:
        hash_key = encoded_pair["hash_key"]
        hash_value = encoded_pair["hash_value"]
        # Safety check
        if len(hash_key) > column_length or len(hash_value) > column_length:
            return None
        
        new_pair = EncodedPair(hash_key, hash_value)
        db_pairs.append(new_pair)
        
    DB.session.add_all(db_pairs)
    # Commit
    DB.session.commit()
    # Return the new message
    return len(db_pairs)
    
def get_message_ids(token, count):
    hash_keys = []
    hash_value_decouplers = []
    for i in xrange(1, count + 1):
        hash_key_message = str(i) + "0"
        hash_key = hash_utils.hmac256(token, hash_key_message)
        hash_keys.append(hash_key)
        
        hash_value_message = str(i) + "1"
        hash_value_decoupler = hash_utils.hmac256(token, hash_value_message)
        hash_value_decouplers.append(hash_value_decoupler)
    
    
    encoded_pairs = EncodedPair.query.filter(EncodedPair.hash_key.in_(hash_keys)).all()

    message_ids = []
    
    
    for ind, encoded_pair in enumerate(encoded_pairs):
        hash_value = encoded_pair.hash_value
        hash_decoupler = hash_value_decouplers[ind]
        message_id = hash_utils.get_id(hash_value, hash_decoupler)
        message_ids.append(message_id)
    
    return message_ids
