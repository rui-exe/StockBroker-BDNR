from fastapi import APIRouter,Query,Path, HTTPException
from app.api.deps import HBase,CurrentUser
from app.crud import financial_instruments as financial_instruments_crud,posts as crud_posts
from app.models.financial_instruments import FinancialInstrument,Tick
from datetime import datetime,timedelta

router = APIRouter()

@router.get("/")
async def get_financial_instruments(db:HBase) -> list[FinancialInstrument]:
  """
  Get all financial instruments
  """
  return financial_instruments_crud.get_symbols(db)

@router.get("/{symbol}")
async def get_financial_instruments_with_params(
    db: HBase,
    symbol: str = Path(..., description="Symbol of the financial instrument"),
    start_date: datetime = Query(..., description="Start date for the interval"),
    end_date: datetime = Query(..., description="End date for the interval"),
    interval: timedelta = Query(..., description="Interval for the tick data")
) -> list[Tick]:
    return financial_instruments_crud.get_instrument_prices(db, symbol, start_date, end_date, interval)

@router.get("/{symbol}/posts")
def get_symbol_posts(db:HBase, symbol:str = Path(..., description="Symbol of the financial instrument")):
  """
  Get the posts of a symbol
  """
  return crud_posts.get_symbol_posts(db, symbol)

@router.post("/{symbol}/posts")
def create_new_post(db: HBase, current_user: CurrentUser, symbol: str = Path(..., description="Symbol of the financial instrument"), text: str = Query(..., description="Text of the post")):
    """
    Create a new post for a symbol.
    """
    if not symbol:
        raise HTTPException(status_code=400, detail="Symbol is required")
    if not text:
        raise HTTPException(status_code=400, detail="Text is required")
    
    post = crud_posts.create_new_post(db, {
        "username": current_user.username,
        "symbol": symbol,
        "text": text
    })
    return post