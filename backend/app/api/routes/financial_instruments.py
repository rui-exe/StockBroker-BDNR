from fastapi import APIRouter,Query,Path, HTTPException
from app.api.deps import HBase,CurrentUser,InstrumentAnalytics
from app.crud import financial_instruments as financial_instruments_crud,posts as crud_posts
from app.models.financial_instruments import FinancialInstrument,Tick
from datetime import datetime,timedelta
from app.hbase_client.hbase_client_pb2 import InstrumentPricesRequest
from google.protobuf.timestamp_pb2 import Timestamp
from google.protobuf.duration_pb2 import Duration

router = APIRouter()

@router.get("/")
async def get_financial_instruments(db:HBase) -> list[FinancialInstrument]:
  """
  Get all financial instruments
  """
  return financial_instruments_crud.get_symbols(db)

@router.get("/{symbol}/prices")
async def get_financial_instruments_with_params(
    instrument_analytics: InstrumentAnalytics,
    symbol: str = Path(..., description="Symbol of the financial instrument"),
    start_date: datetime = Query(..., description="Start date for the timeseries"),
    end_date: datetime = Query(..., description="End date for the timeseries"),
    sampling_period: timedelta = Query(..., description="Time interval for sampling")
) -> list[Tick]:
  
    start_date_timestamp:Timestamp = Timestamp()
    start_date_timestamp.FromDatetime(start_date)

    end_date_timestamp:Timestamp = Timestamp()
    end_date_timestamp.FromDatetime(end_date)
    
    time_delta = Duration()
    time_delta.FromTimedelta(sampling_period)

    grpc_request = InstrumentPricesRequest(
        symbol=symbol,
        start_date=start_date_timestamp,
        end_date=end_date_timestamp,
        time_delta=time_delta
    )

    # Call gRPC method
    grpc_response = instrument_analytics.getInstrumentPrices(grpc_request)

    # Convert gRPC response to Python objects
    ticks = [Tick(timestamp=tick.timestamp.ToDatetime(), value=tick.value) for tick in grpc_response.ticks]

    return ticks

@router.get("/{symbol}/info")
async def get_finstrument_info(db:HBase, symbol:str = Path(..., description="Symbol of the financial instrument")):
  """
  Get the info of a financial instrument
  """
  return financial_instruments_crud.get_symbol_info(db, symbol)

@router.get("/{symbol}/posts")
def get_symbol_posts(db:HBase, symbol:str = Path(..., description="Symbol of the financial instrument"), begin:int=Query(0,description="Begining of the posts")):
  """
  Get the posts of a symbol, 10 at a time
  """
  return crud_posts.get_symbol_posts(db, symbol, begin)

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

@router.get("/{symbol}/price")
async def get_most_recent_price(db:HBase, symbol:str = Path(..., description="Symbol of the financial instrument")) -> Tick:
  """
  Get the most recent price of a financial instrument
  """
  return financial_instruments_crud.get_most_recent_price(db, symbol)