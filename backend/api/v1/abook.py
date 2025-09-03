from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import func
from main import limiter

import schemas
import models
import database
import s3_client
import os

router = APIRouter(
    prefix="/abook",
    tags=["abook"],
)

@router.get("/{qr}/play-auth", response_model=schemas.PlayAuthResponse)
@limiter.limit("20/minute")
def play_auth(request: Request, qr: str, device_id: str, db: Session = Depends(database.get_db)):
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

    # 4. Generate signed URL
    if not qr_code.product or not qr_code.product.title:
        raise HTTPException(status_code=500, detail="Data inconsistency: QR code is not linked to a product/title")

    book_slug = qr_code.product.title.slug
    object_key = f"hls/{book_slug}/master.m3u8"

    ttl_minutes = int(os.getenv("SIGNED_URL_TTL_MIN", 15))

    try:
        signed_url_internal = s3_client.s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': s3_client.S3_BUCKET, 'Key': object_key},
            ExpiresIn=ttl_minutes * 60
        )
        # Rewrite the URL to point to the public-facing proxy
        if s3_client.S3_PUBLIC_ENDPOINT:
            signed_url = signed_url_internal.replace(
                s3_client.S3_ENDPOINT, s3_client.S3_PUBLIC_ENDPOINT
            )
        else:
            signed_url = signed_url_internal

    except Exception as e:
        # Log the error in a real app
        print(f"Error generating presigned URL: {e}")
        raise HTTPException(status_code=500, detail="Could not generate playback URL.")


    return schemas.PlayAuthResponse(
        signed_url=signed_url,
        start_position=start_position,
        title=qr_code.product.title.title,
        author=qr_code.product.title.author,
    )


@router.post("/{qr}/progress", status_code=204)
@limiter.limit("20/minute")
def update_progress(request: Request, qr: str, progress_in: schemas.ProgressRequest, db: Session = Depends(database.get_db)):
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


@router.post("/{qr}/recover", status_code=204)
@limiter.limit("20/minute")
def recover_device_slot(request: Request, qr: str, recover_in: schemas.RecoverRequest, db: Session = Depends(database.get_db)):
    # 1. Find the QR code
    qr_code = db.query(models.QRCode).filter(models.QRCode.qr == qr).first()
    if not qr_code:
        raise HTTPException(status_code=404, detail="QR code not found")

    # 2. Check owner PIN
    # In a real app, use a secure hash comparison (e.g., passlib)
    # For now, we'll do a simple string comparison.
    if qr_code.owner_pin_hash != recover_in.owner_pin:
        raise HTTPException(status_code=403, detail="Invalid PIN")

    # 3. Find active bindings
    active_bindings = db.query(models.DeviceBinding).filter(
        models.DeviceBinding.qr_code_id == qr_code.id,
        models.DeviceBinding.active == True
    ).order_by(models.DeviceBinding.created_at.asc()).all()

    # 4. If 2 or more bindings, deactivate the oldest one
    if len(active_bindings) >= 2:
        oldest_binding = active_bindings[0]
        oldest_binding.active = False
        db.commit()

    return
