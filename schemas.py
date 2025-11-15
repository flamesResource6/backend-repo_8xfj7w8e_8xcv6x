"""
Database Schemas for the Top-up Website

Each Pydantic model corresponds to a MongoDB collection. The collection name is the lowercase of the class name.

Example: class User -> "user"
"""
from typing import Optional, List, Literal
from pydantic import BaseModel, Field, HttpUrl

class Game(BaseModel):
    name: str = Field(..., description="Game title")
    slug: str = Field(..., description="URL friendly identifier")
    publisher: Optional[str] = Field(None, description="Publisher name")
    image: Optional[HttpUrl] = Field(None, description="Cover image URL")
    banner: Optional[HttpUrl] = Field(None, description="Banner image URL")
    tags: List[str] = Field(default_factory=list, description="Searchable tags")

class TopupOption(BaseModel):
    game_slug: str = Field(..., description="Related game slug")
    title: str = Field(..., description="Display title, e.g., 86 Diamonds")
    amount: int = Field(..., ge=1, description="Numeric amount, e.g., diamonds or currency units")
    currency: Literal["IDR"] = Field("IDR", description="Currency code")
    price: int = Field(..., ge=0, description="Price in smallest unit (IDR)")
    popular: bool = Field(False, description="Mark as popular for highlighting")

class Order(BaseModel):
    game_slug: str = Field(..., description="Game slug")
    game_name: str = Field(..., description="Game name for easy rendering")
    user_id: str = Field(..., description="Player ID")
    server: Optional[str] = Field(None, description="Server ID or region if applicable")
    topup_title: str = Field(..., description="Selected top-up option title")
    amount: int = Field(..., description="Selected amount")
    price: int = Field(..., description="Price in IDR")
    payment_method: Literal["QRIS","Dana","OVO","Gopay","Bank Transfer"]
    status: Literal["pending","processing","completed","failed"] = "pending"
    contact: Optional[str] = Field(None, description="Whatsapp/Email for notification")
    note: Optional[str] = Field(None, description="Optional note from user")

class Testimonial(BaseModel):
    name: str
    avatar: Optional[HttpUrl] = None
    message: str
    rating: int = Field(ge=1, le=5, default=5)
    game_slug: Optional[str] = None

class BlogPost(BaseModel):
    title: str
    slug: str
    excerpt: str
    image: Optional[HttpUrl] = None

class FAQ(BaseModel):
    question: str
    answer: str
