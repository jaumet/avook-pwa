from pydantic import BaseModel

class PlayAuthResponse(BaseModel):
    signed_url: str
    start_position: int
    title: str
    author: str

class ProgressRequest(BaseModel):
    device_id: str
    position_sec: int

class RecoverRequest(BaseModel):
    owner_pin: str

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import models

class Token(BaseModel):
    access_token: str
    token_type: str

# --- Admin User Schemas ---

class AdminUserBase(BaseModel):
    email: str
    role: models.RoleEnum

class AdminUserCreate(AdminUserBase):
    password: str

class AdminUser(AdminUserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# --- Title Schemas ---

class TitleBase(BaseModel):
    slug: str
    title: str
    author: Optional[str] = None
    language: Optional[str] = Field(None, max_length=2)
    duration_sec: Optional[int] = None
    cover_path: Optional[str] = None
    status: str = "draft"

class TitleCreate(TitleBase):
    pass

class Title(TitleBase):
    id: int

    class Config:
        orm_mode = True

# --- Product Schemas ---

class ProductBase(BaseModel):
    title_id: int
    sku_ean: Optional[str] = None
    price_cents: Optional[int] = None
    notes: Optional[str] = None

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int
    title: Title

    class Config:
        orm_mode = True


# --- Batch Schemas ---
class BatchCreate(BaseModel):
    name: str
    size: int
    notes: Optional[str] = None

class Batch(BatchCreate):
    id: int
    product_id: int
    printed_at: Optional[datetime] = None

    class Config:
        orm_mode = True

# --- QR Code Schemas ---

class QRCodeBase(BaseModel):
    qr: str
    state: models.QRStateEnum

class QRCode(QRCodeBase):
    id: int
    product_id: int
    batch_id: Optional[int] = None
    created_at: datetime
    image_path: Optional[str] = None

    class Config:
        orm_mode = True

class DeviceBinding(BaseModel):
    id: int
    device_id: str
    created_at: datetime
    last_seen_at: Optional[datetime] = None
    active: bool

    class Config:
        orm_mode = True

class QRCodeDetails(QRCode):
    device_bindings: List[DeviceBinding] = []


class QRCodeMetadata(BaseModel):
    qr_image_name: str
    product_id: str
    date_generation: datetime
    pvp: int
    pvp_currentcy: str
    status: str
    shop_id: Optional[str] = None
    pin: str
    qr_code: str
    avook_url: str
