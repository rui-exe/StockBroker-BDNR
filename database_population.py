import happybase
import time
import yfinance as yf 
import datetime
import csv
import random
import time
import json
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
  """
  Hash a password.
  Args:
    password: The password to hash
  Returns:
    str: The hashed password
  """
  return pwd_context.hash(password)

def wait_for_hbase():
    while True:
        try:
            connection = happybase.Connection(host='localhost', port=9090)
            connection.close()
            break
        except:
            print("HBase is still initializing. Retrying in 5 seconds...")
            time.sleep(5)

def get_symbol_info(ticker):
    return ticker.info['currency'], ticker.info['longName']

def get_historical_data_daily(ticker):
    symbol_historical = ticker.history(period='max', interval='1d')
    return symbol_historical

def get_historical_data_hourly(ticker):
    current_date = datetime.datetime.now().date()
    one_year_ago = current_date - datetime.timedelta(days=365)

    symbol_historical = ticker.history(start=one_year_ago, end=current_date, interval='1h')
    return symbol_historical

def populate_table(connection, table_name, data):
    table = connection.table(table_name)
    print(f"Opened table {table_name}")
    with table.batch() as batch:
        for row, columns in data.items():
            batch.put(row, columns)

def convert_yfinance_symbol_info_to_hbase_dict(symbol,currency,longName):
    data = dict()
    data[symbol.encode("utf-8")] = {
            b'info:name': longName.encode('utf-8'),
            b'info:currency': currency.encode('utf-8')
    }
    return data

def convert_yfinance_price_history_to_hbase_dict(symbol,yahoo_df):
    data = dict()
    for row in yahoo_df.iterrows():
        ticker_timestamp ,(high, low, close, volume, dividends, stock_splits, name) = row
        ticker_datetime = ticker_timestamp.to_pydatetime()
        ticker_datetime_str = ticker_datetime.strftime('%Y-%m-%d %H:%M:%S')
        row_key = f"{symbol}_{ticker_datetime_str}"
        data[row_key.encode("utf-8")] = {
            b'series:val': str(close).encode('utf-8'),
        }
    return data

def populate_users(connection):
    data = dict()
    for row in csv.DictReader(open("datasets/users.csv")):
        username = row['username']
        data[username.encode("utf-8")] = {
            b'info:name': row['name'].encode('utf-8'),
            b'info:password': get_password_hash(['password']).encode('utf-8'),
            b'info:email': row['email'].encode('utf-8')
        }
    populate_table(connection, 'user', data)

def populate_following(connection):
    table = connection.table('user')
    users = list(table.scan())
    data = dict()
    for user, columns in users:
        other_users = [u for u in users if u[0] != user]
        following = random.sample(other_users, random.randint(0, 100))
        following = [(followed_user.decode('utf-8'), _) for followed_user, _ in following]
        data[user] = {f'following:{followed_user}'.encode('utf-8'): b'1' for followed_user, _ in following}
    populate_table(connection, 'user', data)

def populate_posts(connection):
    #get posts from the datasets/stock_tweets.csv Tweet column 
    users = list(connection.table('user').scan())
    data_users = dict()
    data_symbols = dict()
    for row in csv.DictReader(open("datasets/stock_tweets.csv")):
        username = random.choice(users)[0].decode('utf-8')
        post = row['Tweet']
        symbol = row['Stock Name']
        date = row['Date'].split("+")[0]

        if username not in data_users:
            data_users[username] = {}
        user_posts_json = json.dumps({"symbol": symbol, "post": post})
        data_users[username][f'posts:{date}'.encode('utf-8')] = user_posts_json.encode('utf-8')
       
        if symbol not in data_symbols:
            data_symbols[symbol] = {}
        symbol_posts_json = json.dumps({"username": username, "post": post})
        data_symbols[symbol][f'posts:{date}'.encode('utf-8')] = symbol_posts_json.encode('utf-8')

    populate_table(connection, 'user', data_users)
    populate_table(connection, 'financial_instruments', data_symbols)



def populate_financial_instruments(connection,symbols):
    for symbol in symbols:
        print(symbol)
        try:
            ticker = yf.Ticker(symbol)

            
            currency, longName = get_symbol_info(ticker)
            symbol_info = convert_yfinance_symbol_info_to_hbase_dict(symbol,currency,longName)
            populate_table(connection, 'financial_instruments', symbol_info)

            symbol_historical = get_historical_data_daily(ticker)
            symbol_historical_dict = convert_yfinance_price_history_to_hbase_dict(symbol,symbol_historical)
            populate_table(connection, 'instrument_prices', symbol_historical_dict)

            symbol_historical = get_historical_data_hourly(ticker)
            symbol_historical_dict = convert_yfinance_price_history_to_hbase_dict(symbol,symbol_historical)
            populate_table(connection, 'instrument_prices', symbol_historical_dict)
        except Exception as e:
            print(e)

def read_symbols_from_csv(file_name,column_name):
    symbols = []
    with open(file_name, 'r') as csvfile:
        csvreader = csv.DictReader(csvfile)
        for row in csvreader:
            symbols.append(row[column_name])
    return symbols    


def populate_tables():
    wait_for_hbase()
    print("HBase is ready!")
    # Connect to HBase
    connection = happybase.Connection(host='localhost', port=9090)
    print("Connected to HBase")
    
    
    #symbols = ['^GSPC', 'AAPL', 'GOOGL', 'MSFT', 'GME', 'NVDA' , 'KO', 'EDR', 'EDP.LS','FCP.LS']
    #symbols = read_symbols_from_csv("datasets/symbols.csv","Ticker")
    
    #shuffle to avoid hotspots
    #random.shuffle(symbols)

    #get unique Stock Name from the datasets/stock_tweets.csv
    symbols = read_symbols_from_csv("datasets/stock_tweets.csv","Stock Name")
    symbols = list(set(symbols))
    
    
    populate_financial_instruments(connection,symbols)
    populate_users(connection)
    populate_following(connection)
    populate_posts(connection)

if __name__ == "__main__":
    populate_tables()
