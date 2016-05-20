from user import *
from chat import *
from message import *
from encoded_pairs import *

# Create database and tables
DB.create_all()
DB.session.commit()