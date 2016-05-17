from user import *
from message import *
from chat import *
from encoded_pairs import *

# Create database and tables
DB.create_all()
DB.session.commit()