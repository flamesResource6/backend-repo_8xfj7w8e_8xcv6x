import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Game, TopupOption, Order, Testimonial, BlogPost, FAQ

app = FastAPI(title="Indo Game Top-up API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Indo Game Top-up Backend Running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Connected & Working"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else "Unknown"
            response["connection_status"] = "Connected"
            collections = db.list_collection_names()
            response["collections"] = collections[:10]
        else:
            response["database"] = "❌ Not Available"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:120]}"
    return response

# Seed minimal data if empty
@app.on_event("startup")
async def seed_data():
    if db is None:
        return
    if "game" not in db.list_collection_names() or db.game.count_documents({}) == 0:
        games = [
            {"name": "Mobile Legends", "slug": "mobile-legends", "publisher": "Moonton", "tags": ["moba","mlbb","diamonds"], "image": "https://images.unsplash.com/photo-1606112219348-204d7d8b94ee?auto=format&fit=crop&w=800&q=60"},
            {"name": "Free Fire", "slug": "free-fire", "publisher": "Garena", "tags": ["ff","diamonds"], "image": "https://images.unsplash.com/photo-1523961131990-5ea7c61b2107?auto=format&fit=crop&w=800&q=60"},
            {"name": "PUBG Mobile", "slug": "pubg-mobile", "publisher": "Tencent", "tags": ["uc","battle royale"], "image": "https://images.unsplash.com/photo-1542751110-97427bbecf20?auto=format&fit=crop&w=800&q=60"},
            {"name": "Genshin Impact", "slug": "genshin-impact", "publisher": "HoYoverse", "tags": ["genesis crystals"], "image": "https://images.unsplash.com/photo-1548082968-943d8f9d2c37?auto=format&fit=crop&w=800&q=60"},
            {"name": "Honkai Star Rail", "slug": "honkai-star-rail", "publisher": "HoYoverse", "tags": ["stellar jade"], "image": "https://images.unsplash.com/photo-1511512578047-dfb367046420?auto=format&fit=crop&w=800&q=60"}
        ]
        db.game.insert_many(games)
    if "topupoption" not in db.list_collection_names() or db.topupoption.count_documents({}) == 0:
        options = [
            {"game_slug":"mobile-legends","title":"86 Diamonds","amount":86,"currency":"IDR","price":20000,"popular":True},
            {"game_slug":"mobile-legends","title":"172 Diamonds","amount":172,"currency":"IDR","price":38000,"popular":True},
            {"game_slug":"free-fire","title":"100 Diamonds","amount":100,"currency":"IDR","price":20000,"popular":True},
            {"game_slug":"pubg-mobile","title":"60 UC","amount":60,"currency":"IDR","price":15000,"popular":False},
            {"game_slug":"genshin-impact","title":"60 Crystals","amount":60,"currency":"IDR","price":15000,"popular":False},
            {"game_slug":"honkai-star-rail","title":"60 Jade","amount":60,"currency":"IDR","price":15000,"popular":False}
        ]
        db.topupoption.insert_many(options)

# Games
@app.get("/api/games", response_model=List[Game])
def list_games(q: Optional[str] = None):
    if db is None:
        return []
    filter_q = {"$or": [{"name": {"$regex": q, "$options": "i"}}, {"tags": {"$in": [q]}}]} if q else {}
    items = list(db.game.find(filter_q, {"_id": 0}))
    return items

@app.get("/api/games/{slug}", response_model=Optional[Game])
def get_game(slug: str):
    if db is None:
        return None
    item = db.game.find_one({"slug": slug}, {"_id": 0})
    return item

# Top-up options
@app.get("/api/games/{slug}/options", response_model=List[TopupOption])
def get_options(slug: str):
    if db is None:
        return []
    items = list(db.topupoption.find({"game_slug": slug}, {"_id": 0}))
    return items

# Orders
@app.post("/api/orders")
def create_order(order: Order):
    if db is None:
        raise HTTPException(status_code=503, detail="Database unavailable")
    order_id = create_document("order", order)
    return {"order_id": order_id, "status": order.status}

@app.get("/api/orders")
def list_orders(limit: int = 50):
    if db is None:
        return []
    docs = get_documents("order", {}, limit)
    # Convert ObjectId and datetime to strings
    def serialize(d):
        d["_id"] = str(d["_id"]) if "_id" in d else None
        for k, v in list(d.items()):
            if hasattr(v, 'isoformat'):
                d[k] = v.isoformat()
        return d
    return [serialize(d) for d in docs]

# Testimonials
@app.get("/api/testimonials", response_model=List[Testimonial])
def get_testimonials():
    if db is None:
        return [
            {"name":"Adit","message":"Proses cepat, aman, mantap!","rating":5},
            {"name":"Sari","message":"Top-up MLBB cuma 1 menit.","rating":5},
            {"name":"Budi","message":"Harga murah dan terpercaya.","rating":5}
        ]
    items = list(db.testimonial.find({}, {"_id":0}))
    return items

# Blog / Promo
@app.get("/api/blog", response_model=List[BlogPost])
def get_blog():
    if db is None:
        return [
            {"title":"Promo 11.11 Diskon Besar!","slug":"promo-1111","excerpt":"Nikmati diskon hingga 50% untuk semua game.","image":None},
            {"title":"Tips Hemat Top-up","slug":"tips-hemat","excerpt":"Cara hemat top-up tapi tetap puas.","image":None}
        ]
    items = list(db.blogpost.find({}, {"_id":0}))
    return items

# FAQ
@app.get("/api/faq", response_model=List[FAQ])
def get_faq():
    return [
        {"question":"Berapa lama proses top-up?","answer":"Rata-rata 1-5 menit setelah pembayaran terverifikasi."},
        {"question":"Metode pembayaran apa saja?","answer":"QRIS, Dana, OVO, Gopay, dan Transfer Bank."},
        {"question":"Apakah aman?","answer":"100% aman, server resmi dan terenkripsi."}
    ]

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
