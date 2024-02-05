from fastapi import APIRouter
from app.models.test_model import TestModel
from app.schemas.test_schema import TestSchema

router = APIRouter()

@router.get("/test", response_model=TestSchema)
async def get_message():
    # In a real application, you might retrieve this message from a database
    model = TestModel(message="Hello, MVC World!")
    return TestSchema(message=model.get_message())