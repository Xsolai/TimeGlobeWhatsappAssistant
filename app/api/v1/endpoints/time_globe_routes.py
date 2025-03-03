from fastapi import APIRouter, HTTPException, status, Depends
from ....services.time_globe_service import TimeGlobeService
from ....core.dependencies import get_time_globe_service

router = APIRouter()


# @router.post("/get")
# async def get(time_globe_service: TimeGlobeService = Depends(get_time_globe_service)):
#     return time_globe_service.get_sites()


# time_globe_service.book_appointment(
#     email="abdullah.m@xsol.ai",
#     firstname="Abdullah",
#     lastname="Mustafa",
#     gender="Male",
#     mobile_number="+923171546206",
# )
