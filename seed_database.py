"""
AuraStyle - Database Seeder
Run:  python seed_database.py
Inserts exactly 30 fashion products (with CLIP embeddings) into MongoDB.
Skips insertion if products already exist to avoid duplicates.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from database.connection import get_collection
from ai_service import get_text_embedding

# ---------------------------------------------------------------------------
# Product catalogue (30 products across 5 categories × 6 items)
# ---------------------------------------------------------------------------
PRODUCTS = [
    # ── MEN'S FASHION ────────────────────────────────────────────────────────
    {
        "name": "Classic Oxford Button-Down Shirt",
        "brand": "Brooks & Co.",
        "category": "Men's Fashion",
        "gender": "Men",
        "description": "A timeless Oxford-weave button-down in breathable 100% cotton. "
                       "Slim fit with a chest pocket and contrast stitching. Perfect for "
                       "smart-casual office looks or weekend outings.",
        "price": 2499,
        "rating": 4.5,
        "sizes": ["S", "M", "L", "XL", "XXL"],
        "colors": ["White", "Light Blue", "Pink"],
        "material": "100% Cotton",
        "season": "All Season",
        "image_url": "https://images.unsplash.com/photo-1598033129183-c4f50c736f10?w=600",
        "product_url": "#",
    },
    {
        "name": "Slim-Fit Chino Trousers",
        "brand": "Mango Man",
        "category": "Men's Fashion",
        "gender": "Men",
        "description": "Stretch-cotton chinos with a tapered leg cut that transitions "
                       "seamlessly from office to evening. Features slant pockets and a "
                       "clean flat-front waistband.",
        "price": 1999,
        "rating": 4.3,
        "sizes": ["28", "30", "32", "34", "36"],
        "colors": ["Khaki", "Navy", "Olive", "Charcoal"],
        "material": "97% Cotton, 3% Elastane",
        "season": "All Season",
        "image_url": "https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?w=600",
        "product_url": "#",
    },
    {
        "name": "Merino Wool Crew-Neck Sweater",
        "brand": "Uniqlo",
        "category": "Men's Fashion",
        "gender": "Men",
        "description": "Fine-knit merino wool pullover that regulates temperature naturally. "
                       "Ribbed cuffs and hem, classic crew neck. A wardrobe staple in "
                       "muted tones.",
        "price": 3499,
        "rating": 4.7,
        "sizes": ["XS", "S", "M", "L", "XL"],
        "colors": ["Camel", "Grey Melange", "Navy", "Burgundy"],
        "material": "100% Merino Wool",
        "season": "Winter",
        "image_url": "https://images.unsplash.com/photo-1614975059251-992f11792b9f?w=600",
        "product_url": "#",
    },
    {
        "name": "Relaxed Linen Blazer",
        "brand": "Zara Man",
        "category": "Men's Fashion",
        "gender": "Men",
        "description": "Unstructured single-breasted linen blazer with notch lapels and "
                       "two patch pockets. A summer-ready tailored piece that keeps you "
                       "cool in the heat.",
        "price": 4999,
        "rating": 4.4,
        "sizes": ["S", "M", "L", "XL"],
        "colors": ["Ecru", "Sage Green", "Stone"],
        "material": "100% Linen",
        "season": "Summer",
        "image_url": "https://images.unsplash.com/photo-1507679799987-c73779587ccf?w=600",
        "product_url": "#",
    },
    {
        "name": "Raw Denim Straight-Leg Jeans",
        "brand": "Levi's",
        "category": "Men's Fashion",
        "gender": "Men",
        "description": "Japanese selvedge raw denim with zero-wash finish. Straight leg with "
                       "classic five-pocket construction. Fades beautifully with wear.",
        "price": 5999,
        "rating": 4.6,
        "sizes": ["28", "30", "32", "34", "36", "38"],
        "colors": ["Indigo Raw"],
        "material": "100% Selvedge Denim",
        "season": "All Season",
        "image_url": "https://images.unsplash.com/photo-1542272604-787c3835535d?w=600",
        "product_url": "#",
    },
    {
        "name": "Classic Trench Coat",
        "brand": "Burberry Outlet",
        "category": "Men's Fashion",
        "gender": "Men",
        "description": "Double-breasted water-repellent trench coat with storm flap, "
                       "gun patch, and adjustable belt. The quintessential layering piece "
                       "for transitional weather.",
        "price": 12999,
        "rating": 4.8,
        "sizes": ["S", "M", "L", "XL", "XXL"],
        "colors": ["Camel", "Black"],
        "material": "Cotton-Gabardine",
        "season": "Autumn",
        "image_url": "https://images.unsplash.com/photo-1591047139829-d91aecb6caea?w=600",
        "product_url": "#",
    },

    # ── WOMEN'S FASHION ──────────────────────────────────────────────────────
    {
        "name": "Wrap Midi Dress",
        "brand": "& Other Stories",
        "category": "Women's Fashion",
        "gender": "Women",
        "description": "Fluid wrap midi dress in printed viscose-crepe. V-neckline, "
                       "tie-wrap waist, and flared skirt. Effortlessly elegant for brunch "
                       "or evening occasions.",
        "price": 3299,
        "rating": 4.6,
        "sizes": ["XS", "S", "M", "L", "XL"],
        "colors": ["Floral Print", "Cobalt Blue", "Terracotta"],
        "material": "100% Viscose",
        "season": "Spring/Summer",
        "image_url": "https://images.unsplash.com/photo-1515372039744-b8f02a3ae446?w=600",
        "product_url": "#",
    },
    {
        "name": "High-Waist Wide-Leg Trousers",
        "brand": "H&M Conscious",
        "category": "Women's Fashion",
        "gender": "Women",
        "description": "Wide-leg trousers cut from recycled polyester-blend fabric. "
                       "High-rise waistband with invisible zip closure. Pairs with crop "
                       "tops or tucked blouses.",
        "price": 2499,
        "rating": 4.3,
        "sizes": ["XS", "S", "M", "L", "XL", "XXL"],
        "colors": ["Ecru", "Black", "Chocolate Brown"],
        "material": "68% Recycled Polyester, 32% Viscose",
        "season": "All Season",
        "image_url": "https://images.unsplash.com/photo-1583744946564-b52ac1c389c8?w=600",
        "product_url": "#",
    },
    {
        "name": "Satin Slip Blouse",
        "brand": "Massimo Dutti",
        "category": "Women's Fashion",
        "gender": "Women",
        "description": "Bias-cut satin blouse with adjustable spaghetti straps and a "
                       "delicate lace trim hem. Can be dressed up with tailored trousers "
                       "or worn casually over denim.",
        "price": 2799,
        "rating": 4.5,
        "sizes": ["XS", "S", "M", "L"],
        "colors": ["Ivory", "Champagne", "Blush Pink", "Midnight Blue"],
        "material": "100% Silk Satin",
        "season": "All Season",
        "image_url": "https://images.unsplash.com/photo-1551163943-3f6a855d1153?w=600",
        "product_url": "#",
    },
    {
        "name": "Oversized Knit Cardigan",
        "brand": "COS",
        "category": "Women's Fashion",
        "gender": "Women",
        "description": "Relaxed oversized cardigan in a chunky-knit cotton blend. "
                       "Drop-shoulder silhouette, deep pockets, and open-front styling. "
                       "The ultimate cosy-chic layering piece.",
        "price": 3799,
        "rating": 4.7,
        "sizes": ["XS/S", "M/L", "XL/XXL"],
        "colors": ["Oatmeal", "Forest Green", "Rust Orange"],
        "material": "80% Cotton, 20% Wool",
        "season": "Autumn/Winter",
        "image_url": "https://images.unsplash.com/photo-1576566588028-4147f3842f27?w=600",
        "product_url": "#",
    },
    {
        "name": "Pleated Silk Maxi Skirt",
        "brand": "Reformation",
        "category": "Women's Fashion",
        "gender": "Women",
        "description": "Flowing pleated maxi skirt in sustainable Tencel. Elasticated "
                       "waistband and fluid drape. Makes a statement with a simple tucked "
                       "tee or fitted tank.",
        "price": 5299,
        "rating": 4.8,
        "sizes": ["XS", "S", "M", "L", "XL"],
        "colors": ["Dusty Rose", "Sage", "Ivory", "Black"],
        "material": "100% TENCEL Lyocell",
        "season": "Spring/Summer",
        "image_url": "https://images.unsplash.com/photo-1594938298603-c8148c4b4646?w=600",
        "product_url": "#",
    },
    {
        "name": "Tailored Blazer Dress",
        "brand": "Zara",
        "category": "Women's Fashion",
        "gender": "Women",
        "description": "Power-dressing meets minimalism in this single-breasted blazer "
                       "dress with peaked lapels and front welt pockets. Knee-length hem "
                       "and a nipped-waist belt.",
        "price": 4499,
        "rating": 4.5,
        "sizes": ["XS", "S", "M", "L", "XL"],
        "colors": ["Cream", "Black", "Camel"],
        "material": "Polyester-Viscose Blend",
        "season": "All Season",
        "image_url": "https://images.unsplash.com/photo-1490481651871-ab68de25d43d?w=600",
        "product_url": "#",
    },

    # ── FOOTWEAR ─────────────────────────────────────────────────────────────
    {
        "name": "White Leather Low-Top Sneaker",
        "brand": "Common Projects",
        "category": "Footwear",
        "gender": "Unisex",
        "description": "Minimalist full-grain leather sneaker with tonal laces and "
                       "gold serial-number stamp at the heel. Clean lines and supple "
                       "leather that softens with wear.",
        "price": 8999,
        "rating": 4.8,
        "sizes": ["UK 4", "UK 5", "UK 6", "UK 7", "UK 8", "UK 9", "UK 10", "UK 11"],
        "colors": ["White", "Black", "Beige"],
        "material": "Full-Grain Leather",
        "season": "All Season",
        "image_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600",
        "product_url": "#",
    },
    {
        "name": "Chelsea Ankle Boot",
        "brand": "ALDO",
        "category": "Footwear",
        "gender": "Women",
        "description": "Elasticated-panel Chelsea boot in burnished leather with a "
                       "block heel and almond toe. Sleek and versatile — pairs equally "
                       "well with jeans and midi skirts.",
        "price": 5499,
        "rating": 4.4,
        "sizes": ["UK 3", "UK 4", "UK 5", "UK 6", "UK 7", "UK 8"],
        "colors": ["Black", "Tan", "Cognac"],
        "material": "Genuine Leather",
        "season": "Autumn/Winter",
        "image_url": "https://images.unsplash.com/photo-1608256246200-53e635b5b65f?w=600",
        "product_url": "#",
    },
    {
        "name": "Running Shoe Air Zoom Pro",
        "brand": "Nike",
        "category": "Footwear",
        "gender": "Unisex",
        "description": "Responsive React foam midsole with Zoom Air unit in the heel. "
                       "Engineered mesh upper for breathability. Designed for daily "
                       "training runs and long-distance performance.",
        "price": 9999,
        "rating": 4.7,
        "sizes": ["UK 5", "UK 6", "UK 7", "UK 8", "UK 9", "UK 10", "UK 11", "UK 12"],
        "colors": ["Black/White", "Blue/Orange", "Grey/Lime"],
        "material": "Engineered Mesh, Foam, Rubber",
        "season": "All Season",
        "image_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600",
        "product_url": "#",
    },
    {
        "name": "Suede Loafer Mule",
        "brand": "Steve Madden",
        "category": "Footwear",
        "gender": "Women",
        "description": "Backless suede loafer with a penny-keeper vamp and a "
                       "cushioned leather insole. Goes from desk to dinner effortlessly.",
        "price": 3799,
        "rating": 4.3,
        "sizes": ["UK 3", "UK 4", "UK 5", "UK 6", "UK 7"],
        "colors": ["Camel", "Black", "Burgundy"],
        "material": "Suede Upper, Leather Lining",
        "season": "All Season",
        "image_url": "https://images.unsplash.com/photo-1560769629-975ec94e6a86?w=600",
        "product_url": "#",
    },
    {
        "name": "High-Top Canvas Sneaker",
        "brand": "Converse",
        "category": "Footwear",
        "gender": "Unisex",
        "description": "The classic Chuck Taylor All Star in canvas with a medial ankle "
                       "patch and vulcanised rubber sole. Timeless street style icon "
                       "since 1917.",
        "price": 3499,
        "rating": 4.6,
        "sizes": ["UK 4", "UK 5", "UK 6", "UK 7", "UK 8", "UK 9", "UK 10", "UK 11", "UK 12"],
        "colors": ["Black", "Optical White", "Red", "Navy"],
        "material": "Canvas Upper, Rubber Sole",
        "season": "All Season",
        "image_url": "https://images.unsplash.com/photo-1491553895911-0055eca6402d?w=600",
        "product_url": "#",
    },
    {
        "name": "Leather Oxford Brogue",
        "brand": "Clarks",
        "category": "Footwear",
        "gender": "Men",
        "description": "Full-brogue Oxford in Horween leather with Dainite rubber sole. "
                       "Traditional Goodyear-welt construction for resolability and "
                       "long-term durability.",
        "price": 7499,
        "rating": 4.7,
        "sizes": ["UK 6", "UK 7", "UK 8", "UK 9", "UK 10", "UK 11", "UK 12"],
        "colors": ["Dark Tan", "Black", "Mahogany"],
        "material": "Horween Leather, Dainite Sole",
        "season": "Autumn/Winter",
        "image_url": "https://images.unsplash.com/photo-1533867617858-e7b97e060509?w=600",
        "product_url": "#",
    },

    # ── ACCESSORIES ──────────────────────────────────────────────────────────
    {
        "name": "Italian Leather Tote Bag",
        "brand": "Cuyana",
        "category": "Accessories",
        "gender": "Women",
        "description": "Structured vegetable-tanned leather tote with a zip-top closure, "
                       "interior organiser pocket, and detachable pouch. Roomy enough "
                       "for a 13-inch laptop.",
        "price": 11999,
        "rating": 4.8,
        "sizes": ["One Size"],
        "colors": ["Black", "Caramel", "Forest"],
        "material": "Vegetable-Tanned Leather",
        "season": "All Season",
        "image_url": "https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=600",
        "product_url": "#",
    },
    {
        "name": "Silk Square Scarf",
        "brand": "Hermès (Inspired)",
        "category": "Accessories",
        "gender": "Unisex",
        "description": "90 × 90 cm hand-rolled silk twill scarf with a vibrant equestrian "
                       "print. Can be worn around the neck, in the hair, or tied to a "
                       "handbag handle.",
        "price": 6499,
        "rating": 4.6,
        "sizes": ["90 × 90 cm"],
        "colors": ["Orange/Gold", "Blue/White", "Green/Pink"],
        "material": "100% Silk Twill",
        "season": "All Season",
        "image_url": "https://images.unsplash.com/photo-1601924994987-69e26d50dc26?w=600",
        "product_url": "#",
    },
    {
        "name": "Polarised Aviator Sunglasses",
        "brand": "Ray-Ban",
        "category": "Accessories",
        "gender": "Unisex",
        "description": "Classic teardrop aviator frame in gold-tone metal with "
                       "G-15 polarised lenses. UV400 protection. A Hollywood icon "
                       "since 1937.",
        "price": 8499,
        "rating": 4.7,
        "sizes": ["One Size"],
        "colors": ["Gold/G-15 Green", "Silver/Blue", "Gunmetal/Grey"],
        "material": "Metal Frame, Polycarbonate Lens",
        "season": "Summer",
        "image_url": "https://images.unsplash.com/photo-1572635196237-14b3f281503f?w=600",
        "product_url": "#",
    },
    {
        "name": "Minimalist Leather Belt",
        "brand": "Bellroy",
        "category": "Accessories",
        "gender": "Men",
        "description": "Full-grain leather belt with a slim gunmetal box buckle. "
                       "5 adjustment points, 35 mm wide. Designed to look great in "
                       "jeans or trousers.",
        "price": 2999,
        "rating": 4.5,
        "sizes": ["S (70–80 cm)", "M (85–95 cm)", "L (100–110 cm)"],
        "colors": ["Black", "Tan"],
        "material": "Full-Grain Leather",
        "season": "All Season",
        "image_url": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=600",
        "product_url": "#",
    },
    {
        "name": "Ribbed Beanie Hat",
        "brand": "Norse Projects",
        "category": "Accessories",
        "gender": "Unisex",
        "description": "Classic ribbed-knit beanie in a lambswool-acrylic blend. "
                       "Slouchy fit that can be worn cuffed or uncuffed. Embroidered "
                       "brand tab at the cuff.",
        "price": 1499,
        "rating": 4.4,
        "sizes": ["One Size"],
        "colors": ["Charcoal", "Burgundy", "Navy", "Ecru"],
        "material": "50% Lambswool, 50% Acrylic",
        "season": "Winter",
        "image_url": "https://images.unsplash.com/photo-1578020190125-f4f7c18bc9cb?w=600",
        "product_url": "#",
    },
    {
        "name": "Canvas Backpack",
        "brand": "Herschel Supply Co.",
        "category": "Accessories",
        "gender": "Unisex",
        "description": "Durable waxed canvas backpack with a padded 15-inch laptop "
                       "sleeve, fleece-lined sunglasses pocket, and signature striped "
                       "lining. 20-litre capacity.",
        "price": 4499,
        "rating": 4.6,
        "sizes": ["20 L"],
        "colors": ["Black", "Navy Tan", "Camoflage"],
        "material": "Waxed Canvas, Polyester Lining",
        "season": "All Season",
        "image_url": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=600",
        "product_url": "#",
    },

    # ── SPORTSWEAR ───────────────────────────────────────────────────────────
    {
        "name": "Compression Dry-Fit Leggings",
        "brand": "Adidas",
        "category": "Sportswear",
        "gender": "Women",
        "description": "High-waist compression leggings with 4-way stretch AEROREADY "
                       "fabric. Flatlock seams to reduce chafing. Side pocket for "
                       "phone storage.",
        "price": 2999,
        "rating": 4.6,
        "sizes": ["XS", "S", "M", "L", "XL", "XXL"],
        "colors": ["Black", "Navy", "Deep Purple"],
        "material": "78% Polyester, 22% Elastane",
        "season": "All Season",
        "image_url": "https://images.unsplash.com/photo-1506629082955-511b1aa562c8?w=600",
        "product_url": "#",
    },
    {
        "name": "Performance Running Jacket",
        "brand": "Nike",
        "category": "Sportswear",
        "gender": "Men",
        "description": "Lightweight packable windbreaker with a full-zip front and "
                       "reflective detailing for low-light visibility. Stows into its "
                       "own chest pocket.",
        "price": 4799,
        "rating": 4.5,
        "sizes": ["XS", "S", "M", "L", "XL", "XXL"],
        "colors": ["Black", "Electric Blue", "Volt Green"],
        "material": "100% Recycled Polyester",
        "season": "Autumn/Spring",
        "image_url": "https://images.unsplash.com/photo-1512374382149-233c42b6a83b?w=600",
        "product_url": "#",
    },
    {
        "name": "Quick-Dry Sports T-Shirt",
        "brand": "Under Armour",
        "category": "Sportswear",
        "gender": "Men",
        "description": "HeatGear® anti-odour crew-neck tee with moisture-wicking "
                       "microfibre fabric. Ergonomic set-in sleeves for unrestricted "
                       "movement.",
        "price": 1799,
        "rating": 4.4,
        "sizes": ["S", "M", "L", "XL", "XXL"],
        "colors": ["White", "Black", "Red", "Royal Blue"],
        "material": "100% Polyester Microfibre",
        "season": "Summer",
        "image_url": "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=600",
        "product_url": "#",
    },
    {
        "name": "Yoga Flow Sports Bra",
        "brand": "Lululemon",
        "category": "Sportswear",
        "gender": "Women",
        "description": "Medium-support racerback sports bra with a built-in shelf bra, "
                       "removable cups, and four-way Luon® stretch fabric. Sweat-wicking "
                       "and virtually seamless.",
        "price": 3299,
        "rating": 4.7,
        "sizes": ["XS", "S", "M", "L", "XL"],
        "colors": ["Black", "Heather Magenta", "Sage Green"],
        "material": "Luon® (Nylon-Elastane blend)",
        "season": "All Season",
        "image_url": "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=600",
        "product_url": "#",
    },
    {
        "name": "Fleece Zip-Up Hoodie",
        "brand": "Patagonia",
        "category": "Sportswear",
        "gender": "Unisex",
        "description": "Classic full-zip fleece hoodie in 100% recycled polyester. "
                       "Kangaroo pockets, contrast zip-pull, and a regular fit. "
                       "Bluesign® certified fabric.",
        "price": 6999,
        "rating": 4.8,
        "sizes": ["XS", "S", "M", "L", "XL", "XXL"],
        "colors": ["Stone Grey", "Alpine Blue", "Poppy Red"],
        "material": "100% Recycled Polyester Fleece",
        "season": "Autumn/Winter",
        "image_url": "https://images.unsplash.com/photo-1556821840-3a63f15232d0?w=600",
        "product_url": "#",
    },
    {
        "name": "5-Inch Training Shorts",
        "brand": "Gymshark",
        "category": "Sportswear",
        "gender": "Men",
        "description": "Lightweight 5-inch inseam training shorts with an inner brief "
                       "liner, zippered side pockets, and quick-dry fabric. Engineered "
                       "for HIIT, CrossFit, and gym sessions.",
        "price": 2199,
        "rating": 4.5,
        "sizes": ["XS", "S", "M", "L", "XL", "XXL"],
        "colors": ["Black", "Charcoal", "Khaki"],
        "material": "88% Polyester, 12% Elastane",
        "season": "Summer",
        "image_url": "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=600",
        "product_url": "#",
    },
]


def seed():
    col = get_collection("products")

    # Check existing count to avoid duplicates
    existing = col.count_documents({})
    if existing >= len(PRODUCTS):
        print(f"[AuraStyle] Database already contains {existing} products. Skipping seed.")
        return

    print("[AuraStyle] Generating CLIP embeddings — this may take a minute…")
    docs = []
    for idx, product in enumerate(PRODUCTS, start=1):
        # Build a rich text description for CLIP embedding
        text = (
            f"{product['name']} by {product['brand']}. "
            f"Category: {product['category']}. "
            f"Description: {product['description']} "
            f"Colors: {', '.join(product['colors'])}. "
            f"Material: {product['material']}. "
            f"Season: {product['season']}."
        )
        print(f"  [{idx:02d}/{len(PRODUCTS)}] Embedding: {product['name']}")
        embedding = get_text_embedding(text)
        docs.append({**product, "embedding": embedding})

    col.insert_many(docs)
    print(f"\n✅  Successfully inserted {len(docs)} products into MongoDB.")


if __name__ == "__main__":
    seed()
