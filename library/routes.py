from fastapi import APIRouter, Request, HTTPException
from library.models import client_health_reports
from fastapi.responses import HTMLResponse
from library.database import get_db
from datetime import datetime

router = APIRouter()

@router.get("/")
async def ping(request: Request):
    return HTMLResponse("Doctor API Online!")

@router.get("/receive-health-report")
async def get_health_report(request: Request):
    uuid = request.cookies.get("uuid")
    if not uuid:
        raise HTTPException("Missing device UUID")

    report = await request.json()

    with get_db() as session:
        record = client_health_reports(
            device_uuid=uuid,
            date=datetime.now(),
            report=report,
        )
        session.add(record)
        session.commit()

    return HTMLResponse("Health report received", status_code=200)