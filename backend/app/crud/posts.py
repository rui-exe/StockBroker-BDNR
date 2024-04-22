from app.models.posts import Post
from happybase import Connection
from datetime import datetime
import json

def get_user_posts(db:Connection, username:str)->list[Post]:
    user_table = db.table("user")
    posts = []
    for key,data in user_table.row(username.encode("utf-8"),columns=[b"posts"]).items():
        time_stamp = key.decode("utf-8")
        #data is a json
        data = json.loads(data)
        posts.append({
            "username":username,
            "symbol": data["symbol"],
            "timestamp": time_stamp[len("posts:"):],
            "text": data["post"]
        })
    return posts
def get_symbol_posts(db:Connection, symbol:str)->list[Post]:
    symbol_table = db.table("financial_instruments")
    posts = []
    for key,data in symbol_table.row(symbol.encode("utf-8"),columns=[b"posts"]).items():
        time_stamp = key.decode("utf-8")
        #data is a json
        data = json.loads(data)
        posts.append({
            "username": data["username"],
            "symbol": symbol,
            "timestamp": time_stamp[len("posts:"):],
            "text": data["post"]
        })
    return posts
