from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class Station(Base):
    __tablename__ = "stations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)  # Name of the station
    location = Column(String, nullable=False, index=True)  # Physical location
    power_output = Column(Float, nullable=False)  # Maximum power output in kW
    ocpp_id = Column(String, unique=True, nullable=False, index=True)  # Unique OCPP identifier
    status = Column(String, default="Available")  # Status (e.g., Available, InUse, Offline)
    created_at = Column(DateTime, default=datetime.utcnow)  # Creation timestamp
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # Last updated timestamp
    num_chargers = Column(Integer, default=1)  # Number of chargers at the station

    # Relationships
    sessions = relationship("ChargingSession", back_populates="station", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Station(name='{self.name}', location='{self.location}', status='{self.status}')>"


class ChargingSession(Base):
    __tablename__ = "charging_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)  # ID of the user who started the session
    station_id = Column(Integer, ForeignKey("stations.id"), nullable=False)  # Associated station ID
    charger_id = Column(Integer, nullable=False)  # ID of the specific charger within the station
    start_time = Column(DateTime, default=datetime.utcnow)  # Session start time
    end_time = Column(DateTime, nullable=True)  # Session end time
    energy_used = Column(Float, default=0.0)  # Energy consumed in kWh
    cost = Column(Float, default=0.0)  # Cost of the session
    is_active = Column(Boolean, default=True)  # Whether the session is currently active

    # Relationships
    station = relationship("Station", back_populates="sessions")

    def calculate_cost(self, rate_per_kwh: float):
        """Calculates the cost of the session based on energy used and rate per kWh."""
        if self.energy_used:
            self.cost = self.energy_used * rate_per_kwh
        return self.cost

    def __repr__(self):
        return (
            f"<ChargingSession(user_id={self.user_id}, station_id={self.station_id}, "
            f"charger_id={self.charger_id}, energy_used={self.energy_used} kWh, cost=${self.cost})>"
        )
