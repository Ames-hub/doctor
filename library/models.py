from sqlalchemy import Column, Integer, BigInteger, String
from library.database import Base


class boot_drive_health(Base):
    __tablename__ = "boot_drive_health"

    entry_id = Column(Integer, primary_key=True, autoincrement=True)
    drive_id = Column(String)  # Things like /dev/sda
    drive_serial = Column(String)
    timestamp = Column(BigInteger)  # If we use TIMESTAMP, it saves it as a datetime. For our purposes, its easier to store as an int.
    value = Column(Integer)
    days_monitored = Column(Integer)  # How many days we've monitored this drive for