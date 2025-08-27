import os
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import models
import database

def cleanup_inactive_devices(db: Session):
    """
    Job to deactivate device bindings that have been inactive for a long time.
    """
    inactivity_days = int(os.getenv("INACTIVITY_DAYS", 90))
    if inactivity_days <= 0:
        return # Job is disabled

    cutoff_date = datetime.utcnow() - timedelta(days=inactivity_days)

    inactive_bindings = db.query(models.DeviceBinding).filter(
        models.DeviceBinding.active == True,
        models.DeviceBinding.last_seen_at < cutoff_date
    ).all()

    for binding in inactive_bindings:
        binding.active = False

    db.commit()
    print(f"Deactivated {len(inactive_bindings)} inactive device bindings.")
