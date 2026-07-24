from library import models, database
import subprocess
import datetime
import re

def get_drive_serial(device: str) -> str | None:
    """
    Returns the serial number of a drive.
    Returns the drive's serial number, or None if it couldn't be determined.
    """
    result = subprocess.run(
        ["smartctl", "-i", device],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        return None

    match = re.search(r"Serial Number:\s*(.+)", result.stdout)
    if match:
        return match.group(1).strip()

    return None

class drive:
    def __init__(self, drive_id:str):
        """ Expects input like /dev/sda, do not pass a drive serial. """
        self.drive_id = drive_id
        self.drive_serial = get_drive_serial(drive_id)

    def save_current_life(self, life_remaining:int):
        days_monitored = self.calculate_days_monitored()

        with database.get_db() as session:
            record = models.boot_drive_health(
                drive_id=self.drive_id,
                drive_serial=self.drive_serial,
                timestamp=datetime.datetime.now().timestamp(),
                value=life_remaining,
                days_monitored=days_monitored
            )
            session.add(record)
            session.commit()

    def get_current_life(self):
        with database.get_db() as session:
            data = session.query(models.boot_drive_health).filter(
                models.boot_drive_health.drive_id == self.drive_id
            ).order_by(
                models.boot_drive_health.timestamp.desc()
            ).first()

            return data

    def get_history(self, limit:int=None, newest_first:bool=True):
        with database.get_db() as session:
            data = session.query(models.boot_drive_health).filter(
                models.boot_drive_health.drive_id == self.drive_id
            )
            
            if newest_first:
                data = data.order_by(models.boot_drive_health.timestamp.asc())
            else:
                data = data.order_by(models.boot_drive_health.timestamp.desc())

            if limit:
                data = data.limit(limit)

            return data.all()

    def calculate_days_monitored(self):
        oldest = self.get_history(limit=1, newest_first=False)
        if oldest:
            oldest_date = oldest[0].timestamp
            oldest_date = datetime.datetime.fromtimestamp(oldest_date)
            days_monitored = (datetime.datetime.now() - oldest_date).days
        else:
            days_monitored = 0
        return days_monitored

    def purge_history(self):
        with database.get_db() as session:
            items = session.query(models.boot_drive_health).all()
            session.delete(items)
            session.commit()

    def predict_life(self):
        """
        Predicts how many days of life this drive has left before total failure.
        """
        history = self.get_history(limit=31, newest_first=False)

        last_value = None
        last_drive_serial = None
        value_drops = []
        
        for item in history:
            if last_value is None:
                last_value = item.value
                last_timestamp = item.timestamp
                continue
            # Appends by how much it dropped, and how long it took.
            
            if self.drive_serial != last_drive_serial:
                # New drive, purge the history and end this prediction.
                self.purge_history()
                # Return None, as there's less than 7 days of data.
                return None

            last_drive_serial = item.drive_serial

            wear_delta = last_value - item.value
            if wear_delta < 0:
                """
                This means it "healed" from the last value apparently, this isn't correct,
                and is usually the result of an SSDs life span counter thing being more of a "guess" than anything reliable.
                Set it back to 0 for normalcy.
                """
                wear_delta = 0
                 
            value_drops.append(wear_delta)

            last_value = item.value
        
        total_drop = sum(value_drops)
        days_monitored = self.calculate_days_monitored()
        # Prevents divide by 0
        if days_monitored == 0 or total_drop == 0:
            return None
        else:
            wear_per_day = total_drop / days_monitored

        # Prevents divide by 0. Again.
        if wear_per_day <= 0:
            return None
        
        last_value = history[-1].value
        days_remaining = last_value / wear_per_day

        return days_remaining