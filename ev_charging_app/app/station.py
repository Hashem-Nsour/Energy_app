from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app import models, schemas, dependencies
from typing import List

router = APIRouter()

@router.post("/", response_model=schemas.Station, status_code=status.HTTP_201_CREATED)
def create_station(station: schemas.StationCreate, db: Session = Depends(dependencies.get_db)):
    """
    Create a new charging station with the specified details.
    """
    try:
        db_station = models.Station(**station.dict())
        db.add(db_station)
        db.commit()
        db.refresh(db_station)
        return db_station
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Station with these details already exists"
        )


@router.get("/{station_id}", response_model=schemas.Station)
def get_station(station_id: int, db: Session = Depends(dependencies.get_db)):
    """
    Retrieve details of a charging station by its ID.
    """
    station = db.query(models.Station).filter(models.Station.id == station_id).first()
    if not station:
        raise HTTPException(status_code=404, detail="Station not found")
    return station


@router.get("/", response_model=List[schemas.Station])
def list_stations(skip: int = 0, limit: int = 10, db: Session = Depends(dependencies.get_db)):
    """
    Retrieve a paginated list of all charging stations.
    """
    stations = db.query(models.Station).offset(skip).limit(limit).all()
    if not stations:
        raise HTTPException(status_code=404, detail="No stations available")
    return stations


@router.put("/{station_id}", response_model=schemas.Station)
def update_station(station_id: int, station: schemas.StationUpdate, db: Session = Depends(dependencies.get_db)):
    """
    Update details of a specific charging station.
    """
    db_station = db.query(models.Station).filter(models.Station.id == station_id).first()
    if not db_station:
        raise HTTPException(status_code=404, detail="Station not found")
    for key, value in station.dict(exclude_unset=True).items():
        setattr(db_station, key, value)
    db.commit()
    db.refresh(db_station)
    return db_station


@router.delete("/{station_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_station(station_id: int, db: Session = Depends(dependencies.get_db)):
    """
    Delete a charging station by its ID.
    """
    db_station = db.query(models.Station).filter(models.Station.id == station_id).first()
    if not db_station:
        raise HTTPException(status_code=404, detail="Station not found")
    db.delete(db_station)
    db.commit()


@router.put("/{station_id}/activate", response_model=schemas.Station)
def activate_station(station_id: int, db: Session = Depends(dependencies.get_db)):
    """
    Activate a charging station, making it available for users.
    """
    db_station = db.query(models.Station).filter(models.Station.id == station_id).first()
    if not db_station:
        raise HTTPException(status_code=404, detail="Station not found")
    if db_station.is_active:
        raise HTTPException(status_code=400, detail="Station is already active")
    db_station.is_active = True
    db.commit()
    db.refresh(db_station)
    return db_station


@router.put("/{station_id}/deactivate", response_model=schemas.Station)
def deactivate_station(station_id: int, db: Session = Depends(dependencies.get_db)):
    """
    Deactivate a charging station, making it unavailable for users.
    """
    db_station = db.query(models.Station).filter(models.Station.id == station_id).first()
    if not db_station:
        raise HTTPException(status_code=404, detail="Station not found")
    if not db_station.is_active:
        raise HTTPException(status_code=400, detail="Station is already inactive")
    db_station.is_active = False
    db.commit()
    db.refresh(db_station)
    return db_station


@router.get("/{station_id}/sessions", response_model=List[schemas.ChargingSession])
def get_station_sessions(station_id: int, db: Session = Depends(dependencies.get_db)):
    """
    Retrieve all charging sessions associated with a specific station.
    """
    sessions = db.query(models.ChargingSession).filter(models.ChargingSession.station_id == station_id).all()
    if not sessions:
        raise HTTPException(status_code=404, detail="No sessions found for this station")
    return sessions


@router.get("/{station_id}/report", response_model=schemas.StationReport)
def generate_station_report(
        station_id: int,
        start_date: str = None,
        end_date: str = None,
        db: Session = Depends(dependencies.get_db),
):
    """
    Generate a report for a station, summarizing charging sessions, energy used, and total revenue.
    """
    db_station = db.query(models.Station).filter(models.Station.id == station_id).first()
    if not db_station:
        raise HTTPException(status_code=404, detail="Station not found")

    query = db.query(models.ChargingSession).filter(models.ChargingSession.station_id == station_id)

    if start_date:
        query = query.filter(models.ChargingSession.start_time >= start_date)
    if end_date:
        query = query.filter(models.ChargingSession.end_time <= end_date)

    sessions = query.all()
    total_energy = sum(session.energy_used for session in sessions)
    total_revenue = sum(session.cost for session in sessions)

    return schemas.StationReport(
        station_id=station_id,
        total_sessions=len(sessions),
        total_energy=total_energy,
        total_revenue=total_revenue,
        sessions=sessions,
    )
