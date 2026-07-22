from sqlalchemy import Column, Integer, TIMESTAMP, String
from library.database import Base


class boot_drive_health(Base):
    __tablename__ = "boot_drive_health"

    entry_id = Column(Integer, primary_key=True, autoincrement=True)
    drive_id = Column(String)  # Things like /dev/sda
    drive_serial = Column(String)
    timestamp = Column(TIMESTAMP)
    value = Column(Integer)
    days_monitored = Column(Integer)  # How many days we've monitored this drive for