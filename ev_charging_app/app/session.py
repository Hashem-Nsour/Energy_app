from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app import models, schemas, dependencies
from typing import List

router = APIRouter()


@router.post("/sessions/", response_model=schemas.ChargingSession)
def start_charging_session(
        session: schemas.ChargingSessionCreate, db: Session = Depends(dependencies.get_db)
):
    """
    Start a new charging session for a user at a specified station.
    """
    # Validate station availability
    station = db.query(models.Station).filter(models.Station.id == session.station_id).first()
    if not station:
        raise HTTPException(status_code=404, detail="Charging station not found")
    if not station.is_active:
        raise HTTPException(status_code=400, detail="Charging station is inactive")

    # Create and save session
    db_session = models.ChargingSession(
        user_id=session.user_id,
        station_id=session.station_id,
        start_time=datetime.utcnow(),
        energy_used=0.0,
        cost=0.0,
        status="InProgress",
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session


@router.put("/sessions/{session_id}/end", response_model=schemas.ChargingSession)
def end_charging_session(session_id: int, db: Session = Depends(dependencies.get_db)):
    """
    End an active charging session and calculate energy usage and cost.
    """
    # Fetch the active session
    db_session = db.query(models.ChargingSession).filter(models.ChargingSession.id == session_id).first()
    if not db_session or db_session.end_time is not None:
        raise HTTPException(status_code=404, detail="Active session not found")

    # End session
    db_session.end_time = datetime.utcnow()
    duration = (db_session.end_time - db_session.start_time).total_seconds() / 3600  # in hours

    # Simulate energy and cost calculation
    station = db.query(models.Station).filter(models.Station.id == db_session.station_id).first()
    if not station:
        raise HTTPException(status_code=404, detail="Station details not found")

    db_session.energy_used = round(station.power_output * duration, 2)  # e.g., kWh
    db_session.cost = round(db_session.energy_used * station.rate_per_kwh, 2)  # e.g., $

    # Update session status
    db_session.status = "Completed"
    db.commit()
    db.refresh(db_session)
    return db_session


@router.get("/sessions/{session_id}", response_model=schemas.ChargingSession)
def get_charging_session(session_id: int, db: Session = Depends(dependencies.get_db)):
    """
    Retrieve a charging session by its ID.
    """
    db_session = db.query(models.ChargingSession).filter(models.ChargingSession.id == session_id).first()
    if db_session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return db_session


@router.get("/sessions/user/{user_id}", response_model=List[schemas.ChargingSession])
def get_user_sessions(user_id: int, db: Session = Depends(dependencies.get_db)):
    """
    Retrieve all charging sessions for a specific user.
    """
    user_sessions = db.query(models.ChargingSession).filter(models.ChargingSession.user_id == user_id).all()
    if not user_sessions:
        raise HTTPException(status_code=404, detail="No sessions found for this user")
    return user_sessions


@router.get("/sessions/station/{station_id}", response_model=List[schemas.ChargingSession])
def get_station_sessions(station_id: int, db: Session = Depends(dependencies.get_db)):
    """
    Retrieve all charging sessions for a specific station.
    """
    station_sessions = db.query(models.ChargingSession).filter(models.ChargingSession.station_id == station_id).all()
    if not station_sessions:
        raise HTTPException(status_code=404, detail="No sessions found for this station")
    return station_sessions


@router.get("/sessions/", response_model=List[schemas.ChargingSession])
def get_all_sessions(db: Session = Depends(dependencies.get_db)):
    """
    Retrieve all charging sessions (admin view).
    """
    all_sessions = db.query(models.ChargingSession).all()
    return all_sessions


@router.put("/sessions/{session_id}/cancel", response_model=schemas.ChargingSession)
def cancel_charging_session(session_id: int, db: Session = Depends(dependencies.get_db)):
    """
    Cancel an active charging session.
    """
    db_session = db.query(models.ChargingSession).filter(models.ChargingSession.id == session_id).first()
    if not db_session or db_session.end_time is not None:
        raise HTTPException(status_code=404, detail="Active session not found")

    # Mark the session as canceled
    db_session.end_time = datetime.utcnow()
    db_session.status = "Canceled"
    db.commit()
    db.refresh(db_session)
    return db_session


@router.get("/sessions/report/", response_model=schemas.SessionReport)
def generate_session_report(
        station_id: int = None, user_id: int = None, start_date: datetime = None, end_date: datetime = None, db: Session = Depends(dependencies.get_db)
):
    """
    Generate a summary report for sessions filtered by station, user, or date range.
    """
    query = db.query(models.ChargingSession)

    if station_id:
        query = query.filter(models.ChargingSession.station_id == station_id)
    if user_id:
        query = query.filter(models.ChargingSession.user_id == user_id)
    if start_date:
        query = query.filter(models.ChargingSession.start_time >= start_date)
    if end_date:
        query = query.filter(models.ChargingSession.start_time <= end_date)

    sessions = query.all()

    total_energy = sum(session.energy_used for session in sessions)
    total_cost = sum(session.cost for session in sessions)

    return schemas.SessionReport(
        total_sessions=len(sessions),
        total_energy=total_energy,
        total_cost=total_cost,
        sessions=sessions,
    )
