import os
from dotenv import load_dotenv

load_dotenv()
token_vg = os.getenv('token_vk_group')
token_vu = os.getenv('token_vk_user')

conn_driver = os.getenv('conn_driver')
login = os.getenv('login')
password = os.getenv('password')
host = os.getenv('host')
port = os.getenv('port')
db = os.getenv('db')
DSN = f'{conn_driver}://{login}:{password}@{host}:{port}/{db}'