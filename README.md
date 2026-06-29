# AuraStyle — AI-Powered Fashion Discovery

> Multimodal fashion search using **text**, **image**, **voice**, and **combined** queries — powered by OpenAI CLIP and MongoDB Atlas.

---

## Features

| Feature | Details |
|---|---|
| Text Search | CLIP text encoder → cosine similarity |
| Image Search | CLIP image encoder → cosine similarity |
| Voice Search | Web Speech API → CLIP text encoder |
| Multimodal Search | Blended text + image embeddings |
| 30 Products | 5 categories × 6 items, each with CLIP embedding |
| Dark / Light Mode | Persisted via localStorage |
| Filters | Category, Gender, Season, Price, Rating |
| Product Modal | Full detail view with sizes, colors, material |
| Skeleton Loading | Progressive UI feedback |

---

## Tech Stack

- **Frontend**: HTML5, CSS3, Vanilla JS (no frameworks)
- **Backend**: Python Flask + Flask-CORS
- **Database**: MongoDB Atlas (PyMongo)
- **AI**: OpenAI CLIP ViT-B/32 (cosine similarity search)

---

## Quick Start

### 1 — Clone & configure

```bash
git clone <repo>
cd AuraStyle
cp .env.example .env          # edit with your MongoDB URI
```

### 2 — Install Python dependencies

```bash
pip install -r requirements.txt
```

> CLIP installs from GitHub. Requires PyTorch; CPU inference works fine.

### 3 — Seed the database

```bash
python seed_database.py
```

This generates CLIP embeddings for all 30 products and inserts them into MongoDB. Run once — it skips re-insertion if products already exist.

### 4 — Run the server

```bash
python app.py
```

Open **http://localhost:5000** in your browser.

---

## Project Structure

```
AuraStyle/
├── app.py                  # Flask app factory & entry point
├── config.py               # Env-based configuration
├── ai_service.py           # CLIP embedding + cosine similarity
├── seed_database.py        # One-time database seeder (30 products)
├── requirements.txt
├── .env                    # MongoDB URI and secrets (not committed)
│
├── database/
│   ├── connection.py       # PyMongo client
│   ├── models/
│   │   └── product.py      # Query helpers + serialisation
│   └── routes/
│       ├── products.py     # GET /products, GET /product/<id>
│       ├── search.py       # POST /search/* and /voice-search
│       └── upload.py       # POST /upload
│
├── templates/
│   └── index.html          # Single-page frontend
│
└── static/
    ├── css/style.css       # Premium dark-mode stylesheet
    └── js/main.js          # All frontend logic
```

---

## API Reference

| Method | Endpoint | Body / Params | Description |
|--------|----------|--------------|-------------|
| GET | `/products` | `?category=&gender=` | All products |
| GET | `/product/<id>` | — | Single product |
| POST | `/search/text` | `{"query": "..."}` | Text semantic search |
| POST | `/search/image` | `multipart: image` | Image semantic search |
| POST | `/search/multimodal` | `multipart: query + image` | Combined search |
| POST | `/voice-search` | `{"transcript": "..."}` | Voice transcript search |
| POST | `/upload` | `multipart: images` | Upload images, get URLs |
| GET | `/health` | — | Health check |

---

## Product Categories

| Category | Count |
|---|---|
| Men's Fashion | 6 |
| Women's Fashion | 6 |
| Footwear | 6 |
| Accessories | 6 |
| Sportswear | 6 |
| **Total** | **30** |

---

## Environment Variables

```env
MONGO_URI=mongodb+srv://<user>:<pass>@cluster0.xxx.mongodb.net/aurastyle?...
DB_NAME=aurastyle
PORT=5000
```

---

## License

MIT — built for educational demonstration purposes.
