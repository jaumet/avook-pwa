from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
import uuid
import secrets
import csv
import io
import os

import auth
import database
import models
import schemas
import s3_client

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(auth.get_current_admin_user)],
)

# --- Dependency for owner-only routes ---
def get_current_owner(current_user: models.AdminUser = Depends(auth.get_current_admin_user)):
    if current_user.role != models.RoleEnum.owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This action requires owner privileges"
        )
    return current_user

@router.get("/me", response_model=schemas.AdminUser)
async def read_users_me(current_user: models.AdminUser = Depends(auth.get_current_admin_user)):
    """
    Get the current authenticated admin user.
    """
    return current_user

# --- Admin User Management (Owner only) ---

@router.post("/users", response_model=schemas.AdminUser, status_code=status.HTTP_201_CREATED, dependencies=[Depends(get_current_owner)])
def create_admin_user(user: schemas.AdminUserCreate, db: Session = Depends(database.get_db)):
    """
    Create a new admin user (owner only).
    """
    db_user = db.query(models.AdminUser).filter(models.AdminUser.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = auth.get_password_hash(user.password)
    db_user = models.AdminUser(email=user.email, password_hash=hashed_password, role=user.role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.get("/users", response_model=List[schemas.AdminUser], dependencies=[Depends(get_current_owner)])
def read_admin_users(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    """
    Get a list of all admin users (owner only).
    """
    users = db.query(models.AdminUser).offset(skip).limit(limit).all()
    return users

@router.put("/users/{user_id}", response_model=schemas.AdminUser, dependencies=[Depends(get_current_owner)])
def update_admin_user(user_id: int, user_update: schemas.AdminUserBase, db: Session = Depends(database.get_db)):
    """
    Update an admin user's role or email (owner only).
    """
    db_user = db.query(models.AdminUser).filter(models.AdminUser.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if email is being changed to one that already exists
    if user_update.email != db_user.email and db.query(models.AdminUser).filter(models.AdminUser.email == user_update.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    db_user.email = user_update.email
    db_user.role = user_update.role
    db.commit()
    db.refresh(db_user)
    return db_user

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(get_current_owner)])
def delete_admin_user(user_id: int, db: Session = Depends(database.get_db), current_user: models.AdminUser = Depends(get_current_owner)):
    """
    Delete an admin user (owner only).
    """
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete your own user account.")

    db_user = db.query(models.AdminUser).filter(models.AdminUser.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(db_user)
    db.commit()
    return

# --- Title Management ---

@router.post("/titles", response_model=schemas.Title, status_code=status.HTTP_201_CREATED)
def create_title(title: schemas.TitleCreate, db: Session = Depends(database.get_db)):
    db_title = models.Title(**title.dict())
    db.add(db_title)
    db.commit()
    db.refresh(db_title)
    return db_title

@router.get("/titles", response_model=List[schemas.Title])
def read_titles(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    titles = db.query(models.Title).offset(skip).limit(limit).all()
    return titles

@router.get("/titles/{title_id}", response_model=schemas.Title)
def read_title(title_id: int, db: Session = Depends(database.get_db)):
    db_title = db.query(models.Title).filter(models.Title.id == title_id).first()
    if db_title is None:
        raise HTTPException(status_code=404, detail="Title not found")
    return db_title

@router.put("/titles/{title_id}", response_model=schemas.Title)
def update_title(title_id: int, title: schemas.TitleCreate, db: Session = Depends(database.get_db)):
    db_title = db.query(models.Title).filter(models.Title.id == title_id).first()
    if db_title is None:
        raise HTTPException(status_code=404, detail="Title not found")

    for key, value in title.dict().items():
        setattr(db_title, key, value)

    db.commit()
    db.refresh(db_title)
    return db_title

@router.delete("/titles/{title_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_title(title_id: int, db: Session = Depends(database.get_db)):
    db_title = db.query(models.Title).filter(models.Title.id == title_id).first()
    if db_title is None:
        raise HTTPException(status_code=404, detail="Title not found")
    db.delete(db_title)
    db.commit()
    return

@router.post("/titles/{title_id}/upload-cover", response_model=schemas.Title)
def upload_cover_image(title_id: int, file: UploadFile = File(...), db: Session = Depends(database.get_db)):
    db_title = db.query(models.Title).filter(models.Title.id == title_id).first()
    if db_title is None:
        raise HTTPException(status_code=404, detail="Title not found")

    # We can use the title's slug to create a unique and friendly file name
    file_extension = file.filename.split('.')[-1]
    s3_key = f"covers/{db_title.slug}.{file_extension}"

    try:
        s3_client.s3_client.upload_fileobj(
            file.file,
            s3_client.S3_BUCKET,
            s3_key,
            ExtraArgs={'ContentType': file.content_type}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload to S3: {str(e)}")

    # Update the cover_path in the database
    # The path should be the key, so we can construct the full URL later
    db_title.cover_path = s3_key
    db.commit()
    db.refresh(db_title)

    return db_title

# --- Product Management ---

@router.post("/products", response_model=schemas.Product, status_code=status.HTTP_201_CREATED)
def create_product(product: schemas.ProductCreate, db: Session = Depends(database.get_db)):
    # Verify title exists
    db_title = db.query(models.Title).filter(models.Title.id == product.title_id).first()
    if not db_title:
        raise HTTPException(status_code=404, detail=f"Title with id {product.title_id} not found")

    db_product = models.Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@router.get("/products", response_model=List[schemas.Product])
def read_products(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    products = db.query(models.Product).offset(skip).limit(limit).all()
    return products

@router.get("/products/{product_id}", response_model=schemas.Product)
def read_product(product_id: int, db: Session = Depends(database.get_db)):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product

@router.put("/products/{product_id}", response_model=schemas.Product)
def update_product(product_id: int, product: schemas.ProductCreate, db: Session = Depends(database.get_db)):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    # Verify title exists if changed
    if product.title_id != db_product.title_id:
        db_title = db.query(models.Title).filter(models.Title.id == product.title_id).first()
        if not db_title:
            raise HTTPException(status_code=404, detail=f"Title with id {product.title_id} not found")

    for key, value in product.dict().items():
        setattr(db_product, key, value)

    db.commit()
    db.refresh(db_product)
    return db_product

@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, db: Session = Depends(database.get_db)):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(db_product)
    db.commit()
    return

# --- Batch & QR Code Management ---

from sqlalchemy.orm import joinedload

@router.get("/products/{product_id}/batches", response_model=List[schemas.Batch])
def read_product_batches(product_id: int, db: Session = Depends(database.get_db)):
    """
    Get all batches for a specific product.
    """
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail=f"Product with id {product_id} not found")

    return db_product.batches

import zipfile
import json

@router.post("/products/{product_id}/batches", response_model=schemas.Batch)
def create_batch(
    product_id: int,
    batch_create: schemas.BatchCreate,
    db: Session = Depends(database.get_db)
):
    """
    Create a new batch for a product.
    """
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail=f"Product with id {product_id} not found")

    db_batch = models.Batch(
        product_id=product_id,
        name=batch_create.name,
        size=batch_create.size,
        notes=batch_create.notes
    )
    db.add(db_batch)
    db.commit()
    db.refresh(db_batch)
    return db_batch


@router.post("/batches/{batch_id}/upload-qrs", status_code=status.HTTP_201_CREATED)
async def upload_qrs_for_batch(
    batch_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(database.get_db)
):
    """
    Upload a zip file containing QR code PNGs and JSON metadata for a batch.
    The zip file should contain pairs of files named like:
    `YYYY-MM-DD--<qr_code>.json` and `YYYY-MM-DD--<qr_code>.png`
    """
    db_batch = db.query(models.Batch).filter(models.Batch.id == batch_id).first()
    if not db_batch:
        raise HTTPException(status_code=404, detail=f"Batch with id {batch_id} not found")

    if not file.filename.endswith('.zip'):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a .zip file.")

    contents = await file.read()
    zip_buffer = io.BytesIO(contents)

    qr_codes_to_create = []
    duplicates_found = 0
    valid_pairs_found = 0

    with zipfile.ZipFile(zip_buffer, 'r') as zip_ref:
        filenames = zip_ref.namelist()
        json_files = {f for f in filenames if f.endswith('.json') and not f.startswith('__MACOSX/')}
        png_files = {f for f in filenames if f.endswith('.png') and not f.startswith('__MACOSX/')}

        # Create a dictionary for quick lookup of png files by their basename
        png_basenames = {os.path.basename(f): f for f in png_files}

        for json_filename in json_files:
            with zip_ref.open(json_filename) as json_file:
                try:
                    metadata = schemas.QRCodeMetadata.parse_raw(json_file.read())
                except Exception as e:
                    # Log this for debugging purposes
                    print(f"Skipping invalid JSON file {json_filename}: {e}")
                    continue

            # Use the provided image name to locate its PNG file
            expected_png_basename = metadata.qr_image_name

            if expected_png_basename not in png_basenames:
                print(f"No matching PNG found for {json_filename}. Expected: {expected_png_basename}")
                continue

            # Ensure the metadata's product_id matches the batch's product
            if str(metadata.product_id) != str(db_batch.product_id):
                print(
                    f"Metadata product_id {metadata.product_id} does not match batch product {db_batch.product_id} for QR {metadata.qr_code}. Skipping."
                )
                continue

            valid_pairs_found += 1
            png_filename = png_basenames[expected_png_basename]

            # Check for QR code uniqueness
            existing_qr = db.query(models.QRCode).filter(models.QRCode.qr == metadata.qr_code).first()
            if existing_qr:
                duplicates_found += 1
                print(f"QR code {metadata.qr_code} already exists in the database. Skipping.")
                continue

            pin_hash = auth.get_password_hash(str(metadata.pin))
            s3_key = f"qrcodes/{batch_id}/{metadata.qr_code}.png"
            json_key = f"qrcodes/{batch_id}/{metadata.qr_code}.json"

            # Upload PNG to S3
            with zip_ref.open(png_filename) as png_file:
                try:
                    s3_client.s3_client.upload_fileobj(
                        png_file,
                        s3_client.S3_BUCKET,
                        s3_key,
                        ExtraArgs={'ContentType': 'image/png', 'ACL': 'public-read'}
                    )
                except Exception as e:
                    raise HTTPException(status_code=500, detail=f"Failed to upload {png_filename} to S3: {str(e)}")
            # Upload JSON metadata to S3
            with zip_ref.open(json_filename) as metadata_file:
                try:
                    s3_client.s3_client.upload_fileobj(
                        metadata_file,
                        s3_client.S3_BUCKET,
                        json_key,
                        ExtraArgs={'ContentType': "application/json", 'ACL': "public-read"}
                    )
                except Exception as e:
                    raise HTTPException(status_code=500, detail=f"Failed to upload {json_filename} to S3: {str(e)}")


            db_qr_code = models.QRCode(
                product_id=db_batch.product_id,
                qr=metadata.qr_code,
                owner_pin_hash=pin_hash,
                batch_id=batch_id,
                image_path=s3_key,
                state=models.QRStateEnum.new,
            )
            qr_codes_to_create.append(db_qr_code)

    if valid_pairs_found == 0:
        raise HTTPException(status_code=400, detail="No valid QR code files found in the zip archive.")

    if qr_codes_to_create:
        db.bulk_save_objects(qr_codes_to_create)
        db.commit()

    return {"message": f"Upload processed. Created {len(qr_codes_to_create)} new QR codes. Skipped {duplicates_found} duplicates."}

@router.get("/batches/{batch_id}/qrcodes", response_model=List[schemas.QRCode])
def read_batch_qr_codes(batch_id: int, db: Session = Depends(database.get_db)):
    """
    Get all QR codes for a specific batch.
    """
    db_batch = db.query(models.Batch).filter(models.Batch.id == batch_id).first()
    if not db_batch:
        raise HTTPException(status_code=404, detail=f"Batch with id {batch_id} not found")

    return db_batch.qr_codes

@router.get("/qrcodes/{qr}", response_model=schemas.QRCodeDetails)
def read_qr_code_details(qr: str, db: Session = Depends(database.get_db)):
    """
    Get details for a specific QR code, including its state and linked devices.
    """
    db_qr_code = db.query(models.QRCode).options(
        joinedload(models.QRCode.device_bindings)
    ).filter(models.QRCode.qr == qr).first()

    if db_qr_code is None:
        raise HTTPException(status_code=404, detail="QR Code not found")

    return db_qr_code

@router.post("/qrcodes/{qr}/reset", status_code=status.HTTP_204_NO_CONTENT)
def reset_qr_code(qr: str, db: Session = Depends(database.get_db)):
    """
    Reset a QR code: deletes all associated device bindings and sets its state to 'new'.
    """
    db_qr_code = db.query(models.QRCode).filter(models.QRCode.qr == qr).first()
    if db_qr_code is None:
        raise HTTPException(status_code=404, detail="QR Code not found")

    # Delete device bindings
    db.query(models.DeviceBinding).filter(models.DeviceBinding.qr_code_id == db_qr_code.id).delete()

    # Reset state
    db_qr_code.state = models.QRStateEnum.new

    db.commit()
    return
