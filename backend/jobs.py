from sqlalchemy.orm import Session
from database import SessionLocal
import models
import os
from datetime import datetime, timedelta

def seed_initial_data():
    db: Session = SessionLocal()
    try:
        # --- Title ---
        title = db.query(models.Title).filter_by(slug="the-great-gatsby").first()
        if not title:
            title = models.Title(
                title="The Great Gatsby",
                author="F. Scott Fitzgerald",
                slug="the-great-gatsby"
            )
            db.add(title)
            db.commit()
            db.refresh(title)
            print("Seeded title: The Great Gatsby")

        # --- Product ---
        product = db.query(models.Product).filter_by(title_id=title.id).first()
        if not product:
            product = models.Product(
                name="The Great Gatsby - Audiobook",
                title_id=title.id
            )
            db.add(product)
            db.commit()
            db.refresh(product)
            print("Seeded product: The Great Gatsby - Audiobook")

        # --- QR Code 1 ---
        qr_code_1_val = "c2648586c591"
        qr_code_1 = db.query(models.QRCode).filter_by(qr=qr_code_1_val).first()
        if not qr_code_1:
            new_qr_code = models.QRCode(
                product_id=product.id,
                qr=qr_code_1_val,
                owner_pin_hash="1234" # In a real app, this would be a secure hash
            )
            db.add(new_qr_code)
            db.commit()
            print(f"Seeded QR Code: {qr_code_1_val}")

        # --- QR Code 2 ---
        qr_code_2_val = "_R6AE0H6wh"
        qr_code_2 = db.query(models.QRCode).filter_by(qr=qr_code_2_val).first()
        if not qr_code_2:
            new_qr_code = models.QRCode(
                product_id=product.id,
                qr=qr_code_2_val,
                owner_pin_hash="5678" # Different PIN for variety
            )
            db.add(new_qr_code)
            db.commit()
            print(f"Seeded QR Code: {qr_code_2_val}")

    finally:
        db.close()

def cleanup_inactive_devices():
    db: Session = SessionLocal()
    try:
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)

        # Find bindings that are active but haven't been seen in the last 30 days
        inactive_bindings = db.query(models.DeviceBinding).filter(
            models.DeviceBinding.active == True,
            models.DeviceBinding.last_seen_at < thirty_days_ago
        ).all()

        if inactive_bindings:
            for binding in inactive_bindings:
                binding.active = False
            db.commit()
            print(f"Deactivated {len(inactive_bindings)} inactive device bindings.")
        else:
            print("No inactive devices to clean up.")

    finally:
        db.close()
