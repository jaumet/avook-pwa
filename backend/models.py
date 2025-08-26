import enum
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    Enum as SQLAlchemyEnum,
    func,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class RoleEnum(str, enum.Enum):
    owner = "owner"
    editor = "editor"

class QRStateEnum(str, enum.Enum):
    new = "new"
    active = "active"
    blocked = "blocked"

class AdminUser(Base):
    __tablename__ = "admin_users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    role = Column(SQLAlchemyEnum(RoleEnum), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class Title(Base):
    __tablename__ = "titles"
    id = Column(Integer, primary_key=True)
    slug = Column(String, unique=True, nullable=False, index=True)
    title = Column(String, nullable=False)
    author = Column(String)
    language = Column(String(2))
    duration_sec = Column(Integer)
    cover_path = Column(String)
    status = Column(String, default="draft") # e.g., draft, published, archived
    products = relationship("Product", back_populates="title")

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    title_id = Column(Integer, ForeignKey("titles.id"), nullable=False)
    sku_ean = Column(String, unique=True)
    price_cents = Column(Integer)
    notes = Column(String)

    title = relationship("Title", back_populates="products")
    batches = relationship("Batch", back_populates="product")
    qr_codes = relationship("QRCode", back_populates="product")

class Batch(Base):
    __tablename__ = "batches"
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    name = Column(String)
    size = Column(Integer)
    printed_at = Column(DateTime)
    notes = Column(String)

    product = relationship("Product", back_populates="batches")
    qr_codes = relationship("QRCode", back_populates="batch")

class QRCode(Base):
    __tablename__ = "qr_codes"
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    qr = Column(String, unique=True, nullable=False, index=True)
    owner_pin_hash = Column(String)
    batch_id = Column(Integer, ForeignKey("batches.id"))
    state = Column(SQLAlchemyEnum(QRStateEnum), nullable=False, default=QRStateEnum.new)
    created_at = Column(DateTime, server_default=func.now())

    product = relationship("Product", back_populates="qr_codes")
    batch = relationship("Batch", back_populates="qr_codes")
    device_bindings = relationship("DeviceBinding", back_populates="qr_code")
    listening_progress = relationship("ListeningProgress", back_populates="qr_code")


class DeviceBinding(Base):
    __tablename__ = "device_bindings"
    id = Column(Integer, primary_key=True)
    qr_code_id = Column(Integer, ForeignKey("qr_codes.id"), nullable=False)
    device_id = Column(String, nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())
    last_seen_at = Column(DateTime)
    active = Column(Boolean, default=True)

    qr_code = relationship("QRCode", back_populates="device_bindings")

class ListeningProgress(Base):
    __tablename__ = "listening_progress"
    id = Column(Integer, primary_key=True)
    qr_code_id = Column(Integer, ForeignKey("qr_codes.id"), nullable=False)
    device_id = Column(String, nullable=False)
    position_sec = Column(Integer)
    chapter_id = Column(String, nullable=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    qr_code = relationship("QRCode", back_populates="listening_progress")
