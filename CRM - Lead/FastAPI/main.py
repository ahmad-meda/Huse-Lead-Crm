from typing import Union

from fastapi import FastAPI
from lead_value import insert_lead_value # Import your function

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


@app.post("/insert_lead_value/{crm_id}")
def trigger_insert_lead_value(crm_id: str):
    """
    Triggers the insert_lead_value function with the provided CRM ID.
    """
    try:
        insert_lead_value(crm_lead_id=crm_id)
        return {"message": f"Successfully triggered insert_lead_value for CRM ID: {crm_id}"}
    except Exception as e:
        return {"error": f"Failed to trigger insert_lead_value: {e}"}, 500
    

 