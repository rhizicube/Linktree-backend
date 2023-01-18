from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import session
from schemas.subscriptions import RequestSubscription, ResponseSubscription, UpdateSubscription
import crud.subscriptions as subscriptions


from db_connect.setup import get_db

subscription_router = APIRouter()

@subscription_router.post("/subscriptions/")
async def create(request:RequestSubscription, db:session=Depends(get_db)):
    """Async function to create profile

    Args:
        request (RequestProfile): Serialized request data
        db (session, optional): DB connection session for db functionalities. Defaults to Depends(get_db).

    Returns:
        JSONResponse: Profile created with 200 status if profile is created, else exception text with 400 status
    """
    try:
        _subscription = subscriptions.create_subscription(db, request.parameter)
        return JSONResponse(content={"message": f"Subsciption {_subscription.id} created"}, status_code=status.HTTP_201_CREATED)
    except Exception as e:
        print("Error")
        return ResponseSubscription(code=status.HTTP_400_BAD_REQUEST, status="BAD REQUEST", message=str(e)).dict(exclude_none=True)

@subscription_router.get("/subscriptions/")
async def get(id:int=None, db:session=Depends(get_db)):
    try:
        if id:
            _subscription = subscriptions.get_subscription_by_id(db, id)
            if _subscription:
                return ResponseSubscription(code=status.HTTP_200_OK, status="OK", result=_subscription, message="Success").dict(exclude_none=True)
            else:
                return JSONResponse(content={"message": f"Subscription {id} not found"}, status_code=status.HTTP_404_NOT_FOUND)
        else:
            _subscription = subscriptions.get_all_subscriptions(db=db)
            return ResponseSubscription(code=status.HTTP_200_OK, status="OK", result=_subscription, message="Success").dict(exclude_none=True)
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=status.HTTP_400_BAD_REQUEST)

@subscription_router.put("/subscriptions/")
async def update(id:int, request:UpdateSubscription, db:session=Depends(get_db)):
    try:
        _subscription = subscriptions.update_subscription(db, id, request.parameter)
        return JSONResponse(content={"message": f"Subscription {id} updated"}, status_code=status.HTTP_200_OK)
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=status.HTTP_400_BAD_REQUEST)

@subscription_router.delete("/subscriptions/")
async def delete(id:int=None, db:session=Depends(get_db)):
    try:
        if id:
            _subscription = subscriptions.delete_subscription_by_id(db, id)
            return JSONResponse(content={"message": f"Subscription {id} deleted"}, status_code=status.HTTP_200_OK)
        else:
            deleted_rows = subscriptions.delete_all_subscriptions(db)
            return JSONResponse(content={"message": "All subscriptions deleted"}, status_code=status.HTTP_200_OK)
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=status.HTTP_400_BAD_REQUEST)
