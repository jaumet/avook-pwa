from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

import schemas
import models
import database

router = APIRouter(
    prefix="/abook",
    tags=["abook"],
)

@router.get("/{qr}/play-auth", response_model=schemas.PlayAuthResponse)
def play_auth(qr: str, device_id: str, db: Session = Depends(database.get_db)):
    # 1. Find the QR code
    qr_code = db.query(models.QRCode).filter(models.QRCode.qr == qr).first()
    if not qr_code:
        raise HTTPException(status_code=404, detail="QR code not found")

    # 2. Check device bindings
    binding = db.query(models.DeviceBinding).filter(
        models.DeviceBinding.qr_code_id == qr_code.id,
        models.DeviceBinding.device_id == device_id
    ).first()

    if not binding:
        # If not bound, check if we can bind it.
        active_bindings = db.query(models.DeviceBinding).filter(
            models.DeviceBinding.qr_code_id == qr_code.id,
            models.DeviceBinding.active == True
        ).count()

        if active_bindings >= 2:
            raise HTTPException(status_code=403, detail="Device limit reached for this QR code")

        # Create a new binding
        new_binding = models.DeviceBinding(qr_code_id=qr_code.id, device_id=device_id)
        db.add(new_binding)
        db.commit()

    # 3. Get start position (global for the QR code)
    progress = db.query(models.ListeningProgress).filter(
        models.ListeningProgress.qr_code_id == qr_code.id
    ).order_by(models.ListeningProgress.updated_at.desc()).first()

    start_position = progress.position_sec if progress else 0

    # 4. Generate signed URL (placeholder for Fase D)
    # In a real scenario, this would involve a call to S3/MinIO to get a temporary URL.
    # We also need to get the correct path from the product/title associated with the QR code.
    # signed_url = f"https://placeholder.s3.amazonaws.com/hls/{qr_code.product.title.slug}/master.m3u8"
    signed_url = "https://placeholder.url/master.m3u8"


    return schemas.PlayAuthResponse(
        signed_url=signed_url,
        start_position=start_position,
    )


@router.post("/{qr}/progress", status_code=204)
def update_progress(qr: str, progress_in: schemas.ProgressRequest, db: Session = Depends(database.get_db)):
    # 1. Find the QR code
    qr_code = db.query(models.QRCode).filter(models.QRCode.qr == qr).first()
    if not qr_code:
        raise HTTPException(status_code=404, detail="QR code not found")

    # 2. Find the device binding and update last_seen_at
    binding = db.query(models.DeviceBinding).filter(
        models.DeviceBinding.qr_code_id == qr_code.id,
        models.DeviceBinding.device_id == progress_in.device_id
    ).first()

    if not binding or not binding.active:
        raise HTTPException(status_code=403, detail="Device not authorized")

    binding.last_seen_at = func.now()

    # 3. Update or create listening progress for this device
    progress = db.query(models.ListeningProgress).filter(
        models.ListeningProgress.qr_code_id == qr_code.id,
        models.ListeningProgress.device_id == progress_in.device_id
    ).first()

    if progress:
        progress.position_sec = progress_in.position_sec
        progress.updated_at = func.now()
    else:
        progress = models.ListeningProgress(
            qr_code_id=qr_code.id,
            device_id=progress_in.device_id,
            position_sec=progress_in.position_sec,
        )
        db.add(progress)

    db.commit()

    return
