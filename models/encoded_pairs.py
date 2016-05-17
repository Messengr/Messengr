from app import DB
from datetime import datetime

column_length = 100

class EncodedPair(DB.Model):
    __tablename__ = 'encoded_pairs'

    id = DB.Column(DB.Integer, primary_key=True)
    hash_key = DB.Column(DB.String(column_length))
    hash_value = DB.Column(DB.String(column_length))
    
    def __init__(self, hash_key, hash_value):
        self.hash_key = hash_key
        self.hash_value = hash_value
        
    def __repr__(self):
        return '<Encoded Pair %r -> >' % (self.hash_key, self.hash_value)

    def to_dict(self):
        return {
            'id': self.id,
            'hash_key': self.hash_key,
            'hash_value': self.hash_value
        }


def insert_pairs(encoded_pairs):
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
    
def search_pairs(token, count):
    pass
