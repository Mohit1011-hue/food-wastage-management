import pandas as pd
import sqlite3
from urllib.parse import quote_plus
from sqlalchemy import create_engine

# ─── Read from MySQL ──────────────────────────────────────────────────────────
password = quote_plus("M@#!t1011MarU")
mysql_engine = create_engine(f'mysql+mysqlconnector://root:{password}@localhost/food_wastage_db')

providers     = pd.read_sql("SELECT * FROM providers",     mysql_engine)
receivers     = pd.read_sql("SELECT * FROM receivers",     mysql_engine)
food_listings = pd.read_sql("SELECT * FROM food_listings", mysql_engine)
claims        = pd.read_sql("SELECT * FROM claims",        mysql_engine)

print(" Data read from MySQL!")

# ─── Write to SQLite ──────────────────────────────────────────────────────────
sqlite_engine = create_engine('sqlite:///food_wastage.db')

providers.to_sql('providers',         con=sqlite_engine, if_exists='replace', index=False)
receivers.to_sql('receivers',         con=sqlite_engine, if_exists='replace', index=False)
food_listings.to_sql('food_listings', con=sqlite_engine, if_exists='replace', index=False)
claims.to_sql('claims',               con=sqlite_engine, if_exists='replace', index=False)

print(" Data saved to food_wastage.db (SQLite)!")
print(" You can now deploy to Streamlit Cloud!")