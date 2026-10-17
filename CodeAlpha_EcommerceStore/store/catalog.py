"""Sample catalog used by `manage.py seed` and by the product-image generator.

Structure:  CATALOG[category] = {"tint": (bg1, bg2), "sub": {subcategory: [product, ...]}}
Product:    (name, description, price, stock, icon, accent_colour)

`icon` picks the illustration drawn by tools/generate_product_images.py, so every
product image shows the thing the product name says.
"""

CATALOG = {
    "Electronics": {
        "tint": ("#dbeafe", "#e0e7ff"),
        "sub": {
            "Audio": [
                ("Wireless Earbuds", "Bluetooth 5.3 earbuds with noise isolation and a 24-hour charging case.", "1999.00", 40, "earbuds", "#4f46e5"),
                ("Over-Ear Headphones", "Wireless over-ear headphones with active noise cancellation and 40-hour battery life.", "3299.00", 22, "headphones", "#0ea5e9"),
                ("Bluetooth Speaker", "Water-resistant speaker with deep bass and 12-hour playtime.", "1299.00", 35, "speaker", "#ef4444"),
                ("Soundbar 2.1", "Compact 2.1 channel soundbar with wireless subwoofer and HDMI ARC.", "5499.00", 9, "soundbar", "#334155"),
            ],
            "Wearables": [
                ("Smart Watch", "Fitness tracking, heart-rate monitor, and 7-day battery life.", "3499.00", 25, "watch", "#10b981"),
                ("Fitness Band", "Slim fitness tracker with heart-rate, SpO2 and sleep tracking.", "1799.00", 48, "band", "#f43f5e"),
            ],
            "Accessories": [
                ("Portable Power Bank 20000mAh", "Fast-charging power bank with dual USB output.", "1499.00", 60, "powerbank", "#6366f1"),
                ("Mechanical Keyboard", "Compact 75% layout with hot-swappable switches.", "2799.00", 18, "keyboard", "#8b5cf6"),
                ("Wireless Mouse", "Ergonomic 2.4GHz wireless mouse with silent clicks and adjustable DPI.", "699.00", 75, "mouse", "#14b8a6"),
                ("65W USB-C Fast Charger", "GaN wall charger that powers laptops, tablets and phones.", "1599.00", 30, "charger", "#f59e0b"),
            ],
            "Mobiles & Tablets": [
                ("Smartphone 5G 128GB", "6.5-inch AMOLED display, 50MP camera and a 5000mAh battery.", "17999.00", 14, "phone", "#6366f1"),
                ("Tablet 10.4-inch", "10.4-inch display tablet with quad speakers and an 8000mAh battery.", "15499.00", 11, "tablet", "#06b6d4"),
            ],
        },
    },
    "Books": {
        "tint": ("#fef3c7", "#ffedd5"),
        "sub": {
            "Programming": [
                ("Python Crash Course", "A hands-on, project-based introduction to programming with Python.", "699.00", 50, "book", "#2563eb"),
                ("Clean Code", "A handbook of agile software craftsmanship.", "899.00", 30, "book", "#0f766e"),
                ("Introduction to Algorithms", "The classic reference on algorithms and data structures.", "1599.00", 12, "book", "#7c3aed"),
                ("The Pragmatic Programmer", "Your journey to mastery: practical tips for modern software developers.", "1099.00", 20, "book", "#be123c"),
            ],
            "Self-Help": [
                ("Atomic Habits", "Tiny changes, remarkable results: a practical guide to better habits.", "499.00", 80, "book", "#d97706"),
                ("Deep Work", "Rules for focused success in a distracted world.", "549.00", 36, "book", "#0369a1"),
                ("Ikigai", "The Japanese secret to a long and happy life.", "399.00", 55, "book", "#15803d"),
            ],
            "Fiction": [
                ("The Alchemist", "A magical story about following your dreams.", "349.00", 64, "book", "#b45309"),
                ("Wings of Fire", "An autobiography of Dr. A. P. J. Abdul Kalam.", "299.00", 70, "book", "#c2410c"),
            ],
        },
    },
    "Clothing": {
        "tint": ("#fce7f3", "#ede9fe"),
        "sub": {
            "Men": [
                ("Classic Cotton T-Shirt", "Soft, breathable 100% cotton tee in a regular fit.", "399.00", 100, "tshirt", "#3b82f6"),
                ("Slim Fit Jeans", "Stretch denim with a modern slim fit.", "1299.00", 45, "jeans", "#1e40af"),
                ("Formal Cotton Shirt", "Wrinkle-resistant full-sleeve shirt for office and events.", "1099.00", 40, "shirt", "#7dd3fc"),
                ("Cargo Shorts", "Relaxed-fit cotton cargo shorts with six pockets.", "799.00", 52, "shorts", "#6b8e23"),
            ],
            "Women": [
                ("Floral Summer Dress", "Lightweight knee-length dress with a flattering waist.", "1499.00", 26, "dress", "#ec4899"),
                ("Cotton Kurti", "Straight-cut cotton kurti with an embroidered hem.", "899.00", 38, "kurti", "#f97316"),
                ("Yoga Leggings", "High-waist stretch leggings, breathable and squat-proof.", "649.00", 60, "leggings", "#7c3aed"),
            ],
            "Winterwear": [
                ("Hooded Sweatshirt", "Warm fleece-lined hoodie with a kangaroo pocket.", "1199.00", 3, "hoodie", "#64748b"),
                ("Quilted Puffer Jacket", "Lightweight padded jacket that packs small and keeps you warm.", "2799.00", 15, "jacket", "#dc2626"),
            ],
            "Footwear": [
                ("Running Shoes", "Lightweight cushioned shoes for daily runs.", "2499.00", 22, "sneaker", "#2563eb"),
                ("Leather Sandals", "Comfortable leather sandals with a cushioned footbed.", "999.00", 34, "sandal", "#c026d3"),
                ("Formal Leather Shoes", "Classic lace-up oxford shoes in genuine leather.", "2999.00", 17, "shoe", "#78350f"),
            ],
        },
    },
    "Home & Kitchen": {
        "tint": ("#dcfce7", "#ccfbf1"),
        "sub": {
            "Drinkware": [
                ("Stainless Steel Water Bottle", "Insulated 750ml bottle that keeps drinks cold for 24 hours.", "599.00", 70, "bottle", "#0ea5e9"),
                ("Ceramic Coffee Mug Set", "Set of 4 handcrafted 300ml mugs.", "749.00", 28, "mugs", "#f97316"),
                ("Insulated Travel Flask", "Double-wall vacuum flask that keeps drinks hot for 12 hours.", "849.00", 41, "flask", "#14b8a6"),
            ],
            "Lighting": [
                ("LED Desk Lamp", "Dimmable lamp with three colour modes and a USB charging port.", "899.00", 0, "lamp", "#4f46e5"),
                ("String Fairy Lights", "10-metre warm white LED fairy lights for rooms and festivals.", "349.00", 120, "lights", "#f59e0b"),
            ],
            "Cookware": [
                ("Non-stick Frying Pan", "26cm induction-compatible pan with a durable coating.", "999.00", 33, "pan", "#ef4444"),
                ("Pressure Cooker 5L", "Induction-friendly aluminium pressure cooker with a safety valve.", "1799.00", 24, "cooker", "#dc2626"),
                ("Chef's Knife", "8-inch stainless steel knife with an ergonomic handle.", "649.00", 46, "knife", "#1f2937"),
                ("Wooden Cutting Board", "Durable acacia wood board with a juice groove.", "549.00", 31, "board", "#d6a86a"),
            ],
            "Appliances": [
                ("Electric Kettle 1.8L", "Stainless steel kettle with auto shut-off and boil-dry protection.", "899.00", 44, "kettle", "#2563eb"),
                ("2-Slice Pop-up Toaster", "Seven browning levels with defrost and reheat functions.", "1299.00", 19, "toaster", "#ef4444"),
            ],
        },
    },
    "Sports & Fitness": {
        "tint": ("#ffedd5", "#fee2e2"),
        "sub": {
            "Fitness": [
                ("Yoga Mat 6mm", "Non-slip, tear-resistant yoga mat with a carry strap.", "799.00", 58, "mat", "#8b5cf6"),
                ("Dumbbell Set 2 x 5kg", "Rubber-coated hex dumbbells for home workouts.", "1999.00", 20, "dumbbell", "#ef4444"),
            ],
            "Outdoor Games": [
                ("Football Size 5", "Machine-stitched football for training and match play.", "699.00", 40, "football", "#111827"),
                ("Badminton Racket Set", "Two graphite rackets with shuttlecocks and a carry bag.", "1199.00", 27, "racket", "#f97316"),
                ("Cricket Bat", "Kashmir willow bat with a cane handle, ready to play.", "1499.00", 13, "bat", "#2563eb"),
            ],
        },
    },
}


def all_products():
    """Yield (category, subcategory, name, description, price, stock, icon, colour, tint)."""
    for cat, info in CATALOG.items():
        for sub, products in info["sub"].items():
            for name, desc, price, stock, icon, colour in products:
                yield cat, sub, name, desc, price, stock, icon, colour, info["tint"]


# Icon shown next to each category / subcategory name (menu bar, headings, tiles).
CATEGORY_EMOJI = {
    "Electronics": "📱", "Audio": "🎧", "Wearables": "⌚", "Accessories": "🔌", "Mobiles & Tablets": "📱",
    "Books": "📚", "Programming": "💻", "Self-Help": "🌱", "Fiction": "📖",
    "Clothing": "👕", "Men": "👔", "Women": "👗", "Winterwear": "🧥", "Footwear": "👟",
    "Home & Kitchen": "🏠", "Drinkware": "🥤", "Lighting": "💡", "Cookware": "🍳", "Appliances": "🍞",
    "Sports & Fitness": "⚽", "Fitness": "🏋️", "Outdoor Games": "🏏",
}
