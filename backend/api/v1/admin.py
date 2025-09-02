from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
import uuid
import secrets
import csv
import io

import auth
import database
import models
import schemas

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

@router.post("/products/{product_id}/batches", response_class=StreamingResponse)
def create_batch_and_generate_qr_codes(
    product_id: int,
    request: schemas.GenerateQRCodesRequest,
    db: Session = Depends(database.get_db)
):
    """
    Create a new batch for a product and generate N QR codes with PINs.
    Returns a CSV file with the QR codes and plain-text PINs for one-time download.
    """
    # Verify product exists
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail=f"Product with id {product_id} not found")

    # Create the batch
    db_batch = models.Batch(
        product_id=product_id,
        name=request.name,
        size=request.quantity
    )
    db.add(db_batch)
    db.commit()
    db.refresh(db_batch)

    qr_codes_to_create = []
    qr_pin_pairs = []

    for _ in range(request.quantity):
        qr_code_str = str(uuid.uuid4())
        # Generate a 4-digit PIN
        pin = str(secrets.randbelow(10000)).zfill(4)
        pin_hash = auth.get_password_hash(pin)

        qr_pin_pairs.append({"qr": qr_code_str, "pin": pin})

        db_qr_code = models.QRCode(
            product_id=product_id,
            qr=qr_code_str,
            owner_pin_hash=pin_hash,
            batch_id=db_batch.id,
            state=models.QRStateEnum.new,
        )
        qr_codes_to_create.append(db_qr_code)

    db.bulk_save_objects(qr_codes_to_create)
    db.commit()

    # Create CSV response
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["qr_code", "pin"])
    for pair in qr_pin_pairs:
        writer.writerow([pair["qr"], pair["pin"]])

    output.seek(0)

    response = StreamingResponse(iter([output.getvalue()]), media_type="text/csv")
    response.headers["Content-Disposition"] = f"attachment; filename=qrcodes_batch_{db_batch.id}.csv"

    return response

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
