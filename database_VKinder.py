import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, Session
from sqlalchemy import MetaData, create_engine
import os
from dotenv import load_dotenv

load_dotenv()

conn_driver = os.getenv('conn_driver')
login = os.getenv('login')
password = os.getenv('password')
host = os.getenv('host')
port = os.getenv('port')
db = os.getenv('db')
DSN = f'{conn_driver}://{login}:{password}@{host}:{port}/{db}'

engine = sq.create_engine(DSN)

metadata = MetaData()
Base = declarative_base()

class Viewed(Base):
    __tablename__ = 'viewed'
    profile_id = sq.Column(sq.Integer, primary_key=True)
    worksheet_id = sq.Column(sq.Integer, primary_key=True)

    def __str__(self):
        return f'ID пользователя {self.profile_id}, ID найденного пользователя {self.worksheet_id}'

def add_user(engine, profile_id, worksheet_id):
    with Session(engine) as session:
        to_bd = Viewed(profile_id=profile_id, worksheet_id=worksheet_id)
        session.add(to_bd)
        session.commit()

def check_user(engine, profile_id, worksheet_id):
    with Session(engine) as session:
        from_bd = session.query(Viewed).filter(Viewed.profile_id == profile_id,
                                               Viewed.worksheet_id == worksheet_id).first()
        return True if from_bd else False
