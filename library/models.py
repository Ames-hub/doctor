from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Boolean
from library.database import Base

class boot_drive_health(Base):
    __tablename__ = "boot_drive_health"

    entry_id = Column(Integer, primary_key=True, autoincrement=True)
    drive_id = Column(String)  # Things like /dev/sda
    drive_serial = Column(String)
    timestamp = Column(BigInteger)  # If we use TIMESTAMP, it saves it as a datetime. For our purposes, its easier to store as an int.
    value = Column(Integer)
    days_monitored = Column(Integer)  # How many days we've monitored this drive for

class task_execution(Base):
    __tablename__ = "task_executions"

    uuid = Column(String, primary_key=True)
    time = Column(BigInteger, nullable=False)

class check_execution(Base):
    __tablename__ = "check_executions"

    run_id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(BigInteger, nullable=False)
    passed = Column(Boolean, nullable=False)
    issues = Column(String, default=None)

class client_health_reports(Base):
    __tablename__ = "received_health_reports"

    report_id = Column(Integer, autoincrement=True, primary_key=True)
    device_uuid = Column(String, nullable=False)
    date = Column(DateTime, nullable=False)
    report = Column(String, nullable=False)