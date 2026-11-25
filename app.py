# app.py - Garia Misthanna Bhandar - Menu + Submenu + Ordering + Payment in Python (Flask)
# ============================================================
# Run:
#   pip install flask
#   python app.py
# Open: http://127.0.0.1:5000
# Features:
#   Menu + Submenu (Hover) + Cart + Checkout + PAYMENT (COD / UPI / Card - Razorpay) + Order Success + WhatsApp
# ============================================================

from flask import Flask, render_template_string, request, redirect, session, url_for, jsonify
import urllib.parse, json, os, hashlib, hmac, time, random, string
from datetime import datetime

app = Flask(__name__)
app.secret_key = "garia-misthanna-2026-secret-payment"

# ============================================================
# 0. SHOP + PAYMENT CONFIG - EKHANE TOMAR DETAILS BOSAO
# ============================================================
WHATSAPP = "919920225478"  # <-- Tomar WhatsApp: 91 + 10 digit
SHOP_NAME = "Narayan Misthanna Bhandar"
SHOP_ADDRESS = "Garia Station Road, Garia, Kolkata - 700084"
SHOP_TIME = "7 AM - 10 PM"

# --- UPI PAYMENT - Tomar UPI ID ekhane bosao ---
UPI_ID = "anirban81in@okaxis"  # <-- Example: tomar GPay / PhonePe UPI ID, jemon: 9874512345@okhdfc / 9874512345@paytm
UPI_NAME = "Narayan Misthanna Bhandar"    # <-- UPI te j naam dekhabe
UPI_MERCHANT_CODE = "GARIA123"          # <-- Optional

# --- RAZORPAY - Card / UPI / NetBanking er jonno - https://razorpay.com theke free account kholo ---
# Test Mode e chalao - Real taka katbe na. Live korte chaile - Test key bodle Live key bosao.
RAZORPAY_KEY_ID = "rzp_test_XXXXXXXXXXXX"      # <-- Razorpay Dashboard > Settings > API Keys > Key ID
RAZORPAY_KEY_SECRET = "XXXXXXXXXXXXXXXX"       # <-- Key Secret - Server e thakbe - Frontend e debe na
RAZORPAY_ENABLED = False  # <-- True korle Card payment chalu hobe. False thakle - COD + UPI QR diye cholbe - Razorpay charai

# Delivery
FREE_DELIVERY_MIN = 300
DELIVERY_FEE = 30

# ============================================================
# 1. MENU + SUBMENU DATA
# ============================================================
MENU = [
    {"name": "Home", "url": "/", "submenu": []},
    {"name": "Rosogolla", "url": "/category/rosogolla", "submenu": [
        {"title": "Sponge Rosogolla", "desc": "Halka, Norom - BESTSELLER", "price": "₹12", "url": "/category/rosogolla#sponge"},
        {"title": "Normal Rosogolla", "desc": "Chena, Traditional", "price": "₹10", "url": "/category/rosogolla#normal"},
        {"title": "Rajbhog", "desc": "Boro, Kesar + Kaju", "price": "₹35", "url": "/category/rosogolla#rajbhog"},
        {"title": "Chomchom", "desc": "Lomba, Mawa deoa", "price": "₹20", "url": "/category/rosogolla#chomchom"},
        {"title": "Kheer Rosogolla", "desc": "Dudhe dubano", "price": "₹25", "url": "/category/rosogolla#kheer"},
    ]},
    {"name": "Sandesh", "url": "/category/sandesh", "submenu": [
        {"title": "Normal Sandesh", "desc": "Halka misti", "price": "₹15", "url": "/category/sandesh#normal"},
        {"title": "Jalbhora Sandesh", "desc": "Bhitore Gur - SPECIAL", "price": "₹25", "url": "/category/sandesh#jalbhora"},
        {"title": "Kheer Sandesh", "desc": "Kheer + Chena", "price": "₹20", "url": "/category/sandesh#kheer"},
        {"title": "Chocolate Sandesh", "desc": "Bachha der favourite", "price": "₹25", "url": "/category/sandesh#chocolate"},
        {"title": "Nolen Gur Sandesh", "desc": "Sheetkal er sera", "price": "₹30", "url": "/category/sandesh#nolen"},
    ]},
    {"name": "Kheer & Malai", "url": "/category/kheer-malai", "submenu": [
        {"title": "Rasmalai", "desc": "Dudhe dubano - BESTSELLER", "price": "₹40", "url": "/category/kheer-malai#rasmalai"},
        {"title": "Payesh / Kheer", "desc": "Chal + Dudh + Kaju", "price": "₹60", "url": "/category/kheer-malai#payesh"},
        {"title": "Firni", "desc": "Matir bhar e", "price": "₹50", "url": "/category/kheer-malai#firni"},
        {"title": "Malai Roll", "desc": "Malai + Mawa", "price": "₹30", "url": "/category/kheer-malai#malairoll"},
        {"title": "Rabri", "desc": "Ghono Dudh er sor", "price": "₹80", "url": "/category/kheer-malai#rabri"},
    ]},
    {"name": "Dry & Snacks", "url": "/category/dry-sweets", "submenu": [
        {"title": "Motichur Laddu", "desc": "Biye, Puja - Must", "price": "₹15", "url": "/category/dry-sweets#laddu"},
        {"title": "Kaju Barfi", "desc": "Premium", "price": "₹40", "url": "/category/dry-sweets#barfi"},
        {"title": "Gulab Jamun", "desc": "Gorom - HOT", "price": "₹20", "url": "/category/dry-sweets#gulabjamun"},
        {"title": "Kalakand", "desc": "Norom borfi", "price": "₹25", "url": "/category/dry-sweets#kalakand"},
        {"title": "Singara / Kochuri", "desc": "Sokal er - Gorom", "price": "₹10", "url": "/category/dry-sweets#singara"},
    ]},
    {"name": "Special", "url": "/special", "submenu": [
        {"title": "Combo Box - ₹299", "desc": "10 Roso + 6 Sandesh + 4 Rasmalai", "price": "₹299", "url": "/special#combo"},
        {"title": "Biyer Order", "desc": "100+ pc - Bulk", "price": "Bulk", "url": "/special#biyer"},
        {"title": "Gift Box", "desc": "Puja, Bhai Phonta", "price": "₹499+", "url": "/special#gift"},
        {"title": "Sugar-Free", "desc": "Diabetic der jonno", "price": "₹25", "url": "/special#sugarfree"},
    ]},
]

# ============================================================
# 2. PRODUCTS
# ============================================================
PRODUCTS = {
    "sponge": {"name": "Sponge Rosogolla", "cat": "rosogolla", "cat_name": "Rosogolla", "price": 12, "unit": "pc", "desc": "Halka, norom, ros e vora", "tag": "BESTSELLER", "emoji": "🍯"},
    "normal-roso": {"name": "Normal Rosogolla", "cat": "rosogolla", "cat_name": "Rosogolla", "price": 10, "unit": "pc", "desc": "Chena, Traditional", "tag": "", "emoji": "🍯"},
    "rajbhog": {"name": "Rajbhog", "cat": "rosogolla", "cat_name": "Rosogolla", "price": 35, "unit": "pc", "desc": "Boro, kesar + kaju", "tag": "", "emoji": "👑"},
    "chomchom": {"name": "Chomchom", "cat": "rosogolla", "cat_name": "Rosogolla", "price": 20, "unit": "pc", "desc": "Lomba, mawa deoa", "tag": "", "emoji": "🍬"},
    "kheer-roso": {"name": "Kheer Rosogolla", "cat": "rosogolla", "cat_name": "Rosogolla", "price": 25, "unit": "pc", "desc": "Dudhe dubano", "tag": "", "emoji": "🥛"},
    "normal-sandesh": {"name": "Normal Sandesh", "cat": "sandesh", "cat_name": "Sandesh", "price": 15, "unit": "pc", "desc": "Halka misti", "tag": "", "emoji": "🍮"},
    "jalbhora": {"name": "Jalbhora Sandesh", "cat": "sandesh", "cat_name": "Sandesh", "price": 25, "unit": "pc", "desc": "Bhitore gur / ros", "tag": "SPECIAL", "emoji": "⭐"},
    "kheer-sandesh": {"name": "Kheer Sandesh", "cat": "sandesh", "cat_name": "Sandesh", "price": 20, "unit": "pc", "desc": "Kheer + chena", "tag": "", "emoji": "🍮"},
    "choco-sandesh": {"name": "Chocolate Sandesh", "cat": "sandesh", "cat_name": "Sandesh", "price": 25, "unit": "pc", "desc": "Bachha der favourite", "tag": "", "emoji": "🍫"},
    "nolen": {"name": "Nolen Gur Sandesh", "cat": "sandesh", "cat_name": "Sandesh", "price": 30, "unit": "pc", "desc": "Sheetkal er sera", "tag": "SEASONAL", "emoji": "🍯"},
    "rasmalai": {"name": "Rasmalai", "cat": "kheer-malai", "cat_name": "Kheer & Malai", "price": 40, "unit": "pc", "desc": "Dudhe dubano, kesar", "tag": "BESTSELLER", "emoji": "🥛"},
    "payesh": {"name": "Payesh / Kheer", "cat": "kheer-malai", "cat_name": "Kheer & Malai", "price": 60, "unit": "250g", "desc": "Chal + dudh + kaju", "tag": "", "emoji": "🍚"},
    "firni": {"name": "Firni", "cat": "kheer-malai", "cat_name": "Kheer & Malai", "price": 50, "unit": "pc", "desc": "Matir bhar e", "tag": "", "emoji": "🍧"},
    "malai-roll": {"name": "Malai Roll", "cat": "kheer-malai", "cat_name": "Kheer & Malai", "price": 30, "unit": "pc", "desc": "Malai + mawa", "tag": "", "emoji": "🍥"},
    "rabri": {"name": "Rabri", "cat": "kheer-malai", "cat_name": "Kheer & Malai", "price": 80, "unit": "250g", "desc": "Ghono dudh er sor", "tag": "", "emoji": "🥛"},
    "laddu": {"name": "Motichur Laddu", "cat": "dry-sweets", "cat_name": "Dry & Snacks", "price": 15, "unit": "pc", "desc": "Biye, Puja - Must", "tag": "", "emoji": "🟠"},
    "kaju-barfi": {"name": "Kaju Barfi", "cat": "dry-sweets", "cat_name": "Dry & Snacks", "price": 40, "unit": "pc", "desc": "Kaju diye - Premium", "tag": "", "emoji": "🔶"},
    "gulab": {"name": "Gulab Jamun", "cat": "dry-sweets", "cat_name": "Dry & Snacks", "price": 20, "unit": "pc", "desc": "Gorom, ros e dubano", "tag": "HOT", "emoji": "🟤"},
    "kalakand": {"name": "Kalakand", "cat": "dry-sweets", "cat_name": "Dry & Snacks", "price": 25, "unit": "pc", "desc": "Norom borfi", "tag": "", "emoji": "⬜"},
    "singara": {"name": "Singara / Kochuri", "cat": "dry-sweets", "cat_name": "Dry & Snacks", "price": 10, "unit": "pc", "desc": "Sokal er - Gorom", "tag": "", "emoji": "🥟"},
    "combo299": {"name": "Combo Box - ₹299", "cat": "special", "cat_name": "Special", "price": 299, "unit": "box", "desc": "10 Roso + 6 Sandesh + 4 Rasmalai", "tag": "OFFER", "emoji": "🎁"},
    "gift499": {"name": "Gift Box", "cat": "special", "cat_name": "Special", "price": 499, "unit": "box", "desc": "Puja, Bhai Phonta, Biye", "tag": "", "emoji": "🎁"},
}

COUPONS = {
    "GARIA10": 10,   # 10% off
    "FIRST20": 20,   # 20% off - 1st order
    "PUJA50": 50,    # Flat ₹50 off
    "FREEDEL": 0,    # Delivery FREE - code diye
}

# ============================================================
# 3. CART + PAYMENT HELPERS
# ============================================================
def get_cart(): return session.get("cart", {})
def cart_count(): return sum(get_cart().values())
def cart_subtotal():
    return sum(PRODUCTS[pid]["price"]*qty for pid, qty in get_cart().items() if pid in PRODUCTS)
def get_coupon():
    return session.get("coupon", "")
def coupon_discount(subtotal):
    code = get_coupon()
    if code not in COUPONS: return 0
    if code in ["GARIA10", "FIRST20"]:
        return int(subtotal * COUPONS[code] / 100)
    if code == "PUJA50":
        return min(50, subtotal)
    return 0
def delivery_fee(subtotal_after_discount):
    if subtotal_after_discount >= FREE_DELIVERY_MIN or subtotal_after_discount == 0: return 0
    if get_coupon() == "FREEDEL": return 0
    return DELIVERY_FEE
def cart_grand_total():
    sub = cart_subtotal()
    disc = coupon_discount(sub)
    fee = delivery_fee(sub - disc)
    return sub - disc + fee

def gen_order_id():
    return "GMB" + datetime.now().strftime("%d%m%H%M") + ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))

def make_upi_link(amount, order_id, note="Garia Misthanna Order"):
    # UPI Deep Link - GPay / PhonePe / Paytm khulbe - Taka pathano jabe
    params = {"pa": UPI_ID, "pn": UPI_NAME, "am": str(amount), "cu": "INR", "tn": f"{note} - {order_id}", "tr": order_id}
    return "upi://pay?" + urllib.parse.urlencode(params)

def save_order(order):
    try:
        with open("orders.txt", "a", encoding="utf-8") as f:
            f.write("\n" + "="*60 + "\n" + json.dumps(order, ensure_ascii=False, indent=2) + "\n")
        # orders.json - Admin e list dekhano
        orders = []
        if os.path.exists("orders.json"):
            try:
                with open("orders.json", "r", encoding="utf-8") as f: orders = json.load(f)
            except: orders = []
        orders.insert(0, order)
        with open("orders.json", "w", encoding="utf-8") as f: json.dump(orders, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print("Save order error:", e)

def get_orders():
    if os.path.exists("orders.json"):
        try:
            with open("orders.json", "r", encoding="utf-8") as f: return json.load(f)
        except: return []
    return []

# ============================================================
# 4. BASE HTML - Menu + Submenu + Cart Badge
# ============================================================
BASE = """
<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{{ title }} | {{ shop }}</title>
<script src="https://checkout.razorpay.com/v1/checkout.js"></script>
<style>
*{margin:0;padding:0;box-sizing:border-box;font-family:Arial,sans-serif}
body{background:#FFF7EB;color:#1A1A1A}a{text-decoration:none;color:inherit}
.topbar{background:#8B1E1E;color:#fff;text-align:center;padding:8px;font-size:13px;font-weight:700}.topbar span{color:#FFC107}
header{background:#fff;position:sticky;top:0;z-index:100;box-shadow:0 2px 10px rgba(0,0,0,.08)}
.nav{max-width:1250px;margin:auto;display:flex;align-items:center;justify-content:space-between;padding:12px 16px;gap:12px}
.logo{font-size:24px;font-weight:900;color:#8B1E1E;line-height:1}.logo small{display:block;font-size:10px;color:#888;letter-spacing:2px}.logo em{font-style:normal;color:#FF6B00}
nav ul{list-style:none;display:flex;gap:2px;align-items:center}nav ul li{position:relative}
nav ul li>a{padding:10px 12px;display:flex;gap:5px;font-weight:700;font-size:14px;border-radius:8px;white-space:nowrap}
nav ul li:hover>a{background:#FFF0D9;color:#8B1E1E}
.submenu{position:absolute;top:100%;left:0;min-width:310px;background:#fff;box-shadow:0 10px 30px rgba(0,0,0,.15);border-radius:12px;padding:8px;display:none;z-index:10}
nav ul li:hover>.submenu{display:block}.submenu a{display:flex;gap:10px;padding:11px;border-radius:10px}
.submenu a:hover{background:#FFF7EB}.submenu b{font-size:14px;display:block}.submenu span{font-size:12px;color:#666;display:block}
.submenu .price{margin-left:auto;background:#8B1E1E;color:#fff;font-size:12px;padding:4px 8px;border-radius:20px;white-space:nowrap;font-weight:700}
.btn{background:#1A7A2E;color:#fff!important;padding:11px 16px!important;border-radius:25px;font-weight:800;white-space:nowrap}
.btn-orange{background:#FF6B00}.btn-maroon{background:#8B1E1E}.btn-outline{background:#fff;border:2px solid #8B1E1E;color:#8B1E1E!important}
.cart-btn{position:relative}.cart-badge{position:absolute;top:-6px;right:-6px;background:#FF6B00;color:#fff;font-size:11px;width:20px;height:20px;border-radius:50%;display:flex;align-items:center;justify-content:center}
.hamburger{display:none;font-size:28px;cursor:pointer}#menu-toggle{display:none}
.section{max-width:1250px;margin:28px auto;padding:0 16px}.section h2{font-size:28px;color:#8B1E1E}
.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-top:16px}
.card{background:#fff;border-radius:16px;padding:16px;box-shadow:0 4px 16px rgba(0,0,0,.06);display:flex;flex-direction:column}
.card .emoji{font-size:44px;text-align:center;margin:6px 0}.card h3{font-size:16px}.card p{font-size:13px;color:#666;margin:6px 0;line-height:1.5;flex:1}
.card .tag{font-size:10px;background:#1A7A2E;color:#fff;padding:2px 6px;border-radius:8px}
.price-row{display:flex;justify-content:space-between;align-items:center;margin-top:10px}
.qty-box{display:flex;align-items:center;gap:8px;margin-top:10px}.qty-box a{width:32px;height:32px;border-radius:50%;border:1px solid #ddd;background:#fff;font-size:18px;display:flex;align-items:center;justify-content:center}.qty-box span{font-weight:800}
.add-btn{background:#8B1E1E;color:#fff;padding:9px 14px;border-radius:20px;font-size:13px;font-weight:700;border:none;cursor:pointer;width:100%;margin-top:8px}
.tabs{display:flex;gap:8px;flex-wrap:wrap;margin:14px 0}.tabs a{background:#fff;border:1px solid #E8DCC8;padding:9px 14px;border-radius:20px;font-size:14px;font-weight:700}.tabs a.active,.tabs a:hover{background:#8B1E1E;color:#fff}
table{width:100%;border-collapse:collapse;background:#fff;border-radius:14px;overflow:hidden}th{background:#8B1E1E;color:#fff;text-align:left;padding:12px}td{padding:11px;border-bottom:1px solid #eee;font-size:14px}
input,select,textarea{width:100%;padding:12px;border-radius:10px;border:1px solid #ddd;font-size:15px}
.form-box{background:#fff;padding:22px;border-radius:18px;display:grid;gap:12px}
.pay-option{border:2px solid #eee;border-radius:14px;padding:14px;cursor:pointer;display:flex;gap:12px;align-items:flex-start}
.pay-option:hover{border-color:#8B1E1E}.pay-option.selected{border-color:#1A7A2E;background:#F0FFF4}
.pay-option input{width:auto;margin-top:3px}.pay-option b{font-size:15px}.pay-option small{color:#666;display:block;margin-top:3px;line-height:1.4}
.upi-box{background:#F0FFF4;border:2px dashed #1A7A2E;border-radius:14px;padding:16px;text-align:center;margin-top:12px}
.success{background:#E8FFE8;border:2px solid #1A7A2E;border-radius:18px;padding:24px;text-align:center}
footer{background:#8B1E1E;color:#fff;margin-top:40px}.foot{max-width:1250px;margin:auto;padding:28px 16px;display:grid;grid-template-columns:2fr 1fr 1fr 1fr;gap:20px}.foot a{display:block;padding:4px 0;color:#F5E6D0;font-size:14px}.foot p{font-size:14px;color:#F5E6D0;line-height:1.6}
.float{position:fixed;right:16px;bottom:16px;background:#25D366;color:#fff;padding:12px 16px;border-radius:30px;font-weight:800;z-index:99}
@media(max-width:900px){.grid{grid-template-columns:1fr 1fr}.foot{grid-template-columns:1fr 1fr}.hamburger{display:block}nav{position:absolute;top:100%;left:0;right:0;background:#fff;display:none;max-height:70vh;overflow:auto} #menu-toggle:checked+nav{display:block}nav ul{flex-direction:column;align-items:stretch;padding:10px}.submenu{position:static;box-shadow:none;display:block;padding-left:14px}}
@media(max-width:500px){.grid{grid-template-columns:1fr}}
</style></head><body>
<div class="topbar">Garia Station Road • 7 AM - 10 PM • <span>₹300+ e FREE Delivery • COD / UPI / Card - Sob Payment</span></div>
<header><div class="nav"><a href="/" class="logo">GARIA <em>MISTHANNA</em><small>BHANDAR • GARIA</small></a>
<label for="menu-toggle" class="hamburger">☰</label><input type="checkbox" id="menu-toggle">
<nav><ul>
{% for item in menu %}<li><a href="{{ item.url }}">{{ item.name }}{% if item.submenu %} ▼{% endif %}</a>
{% if item.submenu %}<div class="submenu">{% for sub in item.submenu %}
<a href="{{ sub.url }}"><div><b>{{ sub.title }}</b><span>{{ sub.desc }}</span></div><span class="price">{{ sub.price }}</span></a>
{% endfor %}</div>{% endif %}</li>{% endfor %}
<li><a href="/cart" class="btn btn-orange cart-btn">🛒 Cart {% if cart_count>0 %}<span class="cart-badge">{{ cart_count }}</span>{% endif %}</a></li>
<li><a href="/checkout" class="btn">Pay & Order</a></li>
</ul></nav></div></header>
{{ content | safe }}
<footer><div class="foot"><div><h4>GARIA MISTHANNA BHANDAR</h4><p>📍 {{ address }}<br>📞 WhatsApp: {{ whatsapp }}<br>⏰ {{ time }}<br>💳 Payment: COD / UPI / Card</p></div>
<div><h4>Menu</h4><a href="/category/rosogolla">Rosogolla</a><a href="/category/sandesh">Sandesh</a><a href="/category/kheer-malai">Kheer & Malai</a><a href="/category/dry-sweets">Dry & Snacks</a></div>
<div><h4>Help</h4><a href="/about">Our Story</a><a href="/faq">FAQ</a><a href="/contact">Contact</a><a href="/admin">Admin</a></div>
<div><h4>Order</h4><a href="/cart">My Cart</a><a href="/checkout">Checkout + Payment</a><a href="/orders">My Orders</a><a href="/special">Combo ₹299</a></div></div>
<div style="text-align:center;padding:14px;font-size:12px;border-top:1px solid rgba(255,255,255,.2)">© 2026 {{ shop }} • Garia, Kolkata • Secure Payment</div></footer>
<a class="float" href="https://wa.me/{{ whatsapp }}?text=Hi!%20Misti%20Order" target="_blank">💬 Order on WhatsApp</a>
</body></html>
"""

def render_page(title, content):
    return render_template_string(BASE, title=title, shop=SHOP_NAME, menu=MENU, whatsapp=WHATSAPP,
                                  address=SHOP_ADDRESS, time=SHOP_TIME, cart_count=cart_count(), content=content)

def product_card(pid, p):
    qty = get_cart().get(pid, 0)
    tag_html = f'<span class="tag">{p["tag"]}</span> ' if p["tag"] else ""
    if qty > 0:
        qty_html = f"""<div class="qty-box"><a href="/cart/remove/{pid}">−</a><span>{qty}</span><a href="/cart/add/{pid}">+</a><span style="margin-left:auto;color:#8B1E1E">₹{p['price']*qty}</span></div>"""
    else:
        qty_html = f"""<a href="/cart/add/{pid}"><button class="add-btn">+ Add to Cart - ₹{p['price']}</button></a>"""
    return f"""<div class="card"><div class="emoji">{p['emoji']}</div><h3>{tag_html}{p['name']}</h3><p>{p['desc']}<br><small>{p['cat_name']} • ₹{p['price']} / {p['unit']}</small></p><div class="price-row"><b>₹{p['price']} / {p['unit']}</b></div>{qty_html}</div>"""

# ============================================================
# 5. HOME + CATEGORY
# ============================================================
@app.route("/")
def home():
    featured = ["sponge", "jalbhora", "rasmalai", "gulab", "rajbhog", "nolen", "combo299", "laddu"]
    cards = "".join(product_card(pid, PRODUCTS[pid]) for pid in featured)
    content = f"""
    <section class="section"><h2>Garia er Sera Misti - Protidin Taza 🍯</h2>
    <p>Menu te hover korle submenu khulbe. Add to Cart → Checkout → Payment (COD / UPI / Card) → Order Done.</p>
    <div class="tabs"><a href="/" class="active">Bestseller</a><a href="/category/rosogolla">Rosogolla</a><a href="/category/sandesh">Sandesh</a><a href="/category/kheer-malai">Kheer & Malai</a><a href="/category/dry-sweets">Dry & Snacks</a><a href="/special">Combo ₹299</a></div>
    <div class="grid">{cards}</div>
    <div style="background:#fff;padding:20px;border-radius:16px;margin-top:20px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px">
      <div><h3>💳 Payment - 3 te Option</h3><p>COD (Cash) • UPI (GPay / PhonePe) • Card (Razorpay) - Coupon: <b>GARIA10</b> = 10% OFF</p></div>
      <a href="/cart" style="background:#8B1E1E;color:#fff;padding:12px 18px;border-radius:25px;font-weight:800">🛒 Go to Cart →</a>
    </div></section>"""
    return render_page("Home", content)

@app.route("/category/<cat>")
def category(cat):
    cats = {"rosogolla": "Rosogolla", "sandesh": "Sandesh", "kheer-malai": "Kheer & Malai", "dry-sweets": "Dry & Snacks", "special": "Special"}
    if cat not in cats: return redirect("/")
    items = [(pid, p) for pid, p in PRODUCTS.items() if p["cat"] == cat]
    cards = "".join(product_card(pid, p) for pid, p in items)
    content = f"""<section class="section"><h2>{cats[cat]} - Full Menu</h2><div class="grid">{cards}</div>
    <p style="margin-top:18px"><a href="/cart" style="background:#1A7A2E;color:#fff;padding:12px 18px;border-radius:25px;font-weight:800;display:inline-block">🛒 Go to Cart ({cart_count()}) →</a></p></section>"""
    return render_page(cats[cat], content)

@app.route("/special")
def special():
    cards = "".join(product_card(pid, PRODUCTS[pid]) for pid in ["combo299", "gift499"])
    return render_page("Special", f"""<section class="section"><h2>Special / Combo / Biyer Order</h2><div class="grid">{cards}</div>
    <div style="background:#fff;padding:20px;border-radius:16px;margin-top:20px"><h3>Biyer Order - Bulk - Advance Payment</h3><p style="margin:10px 0">100+ pc hole - 50% Advance UPI te dite hobe. Baki ta delivery te Cash. WhatsApp koro.</p>
    <a href="https://wa.me/{WHATSAPP}?text=Biyer%20Order%20-%20Advance%20Payment" style="background:#25D366;color:#fff;padding:12px 18px;border-radius:25px;font-weight:800;display:inline-block">WhatsApp e Biyer Order →</a></div></section>""")

# ============================================================
# 6. CART + COUPON
# ============================================================
@app.route("/cart/add/<pid>")
def add_to_cart(pid):
    if pid in PRODUCTS:
        cart = get_cart(); cart[pid] = cart.get(pid, 0) + 1; session["cart"] = cart
    return redirect(request.referrer or "/")
@app.route("/cart/remove/<pid>")
def remove_from_cart(pid):
    cart = get_cart()
    if pid in cart:
        cart[pid] -= 1
        if cart[pid] <= 0: del cart[pid]
        session["cart"] = cart
    return redirect(request.referrer or "/cart")
@app.route("/cart/delete/<pid>")
def delete_from_cart(pid):
    cart = get_cart()
    if pid in cart: del cart[pid]; session["cart"] = cart
    return redirect("/cart")
@app.route("/cart/clear")
def clear_cart(): session["cart"] = {}; session["coupon"] = ""; return redirect("/cart")

@app.route("/coupon", methods=["POST"])
def apply_coupon():
    code = request.form.get("coupon", "").strip().upper()
    if code in COUPONS:
        session["coupon"] = code
        session["coupon_msg"] = f"✅ Coupon {code} applied!"
    else:
        session["coupon"] = ""
        session["coupon_msg"] = "❌ Coupon thik na - Try: GARIA10 / FIRST20 / PUJA50"
    return redirect("/cart")

@app.route("/cart")
def cart_page():
    cart = get_cart()
    if not cart:
        return render_page("Cart", """<section class="section"><h2>🛒 Cart - Khali</h2><p style="margin-top:10px">Menu theke Add to Cart koro.</p><p style="margin-top:14px"><a href="/" style="background:#8B1E1E;color:#fff;padding:12px 18px;border-radius:25px;font-weight:800;display:inline-block">← Menu Dekho</a></p></section>""")
    rows = ""
    for pid, qty in cart.items():
        p = PRODUCTS[pid]
        rows += f"""<tr><td>{p['emoji']} <b>{p['name']}</b><br><small>₹{p['price']} / {p['unit']}</small></td>
        <td><a href="/cart/remove/{pid}" style="font-size:20px;padding:4px 10px;border:1px solid #ddd;border-radius:50%">−</a> <b>{qty}</b> <a href="/cart/add/{pid}" style="font-size:20px;padding:4px 10px;border:1px solid #ddd;border-radius:50%">+</a></td>
        <td style="text-align:right">₹{p['price']*qty}</td><td style="text-align:right"><a href="/cart/delete/{pid}" style="color:#D92B1F">✕</a></td></tr>"""
    sub = cart_subtotal(); disc = coupon_discount(sub); fee = delivery_fee(sub - disc); grand = sub - disc + fee
    coupon_msg = session.pop("coupon_msg", "")
    content = f"""
    <section class="section"><h2>🛒 My Cart - {cart_count()} items</h2>
    <div style="overflow-x:auto;margin-top:14px"><table><tr><th>Item</th><th>Qty</th><th style="text-align:right">Total</th><th></th></tr>{rows}</table></div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:16px;align-items:start">
      <div style="background:#fff;padding:20px;border-radius:16px">
        <h3>🎟️ Coupon Code</h3>
        <form method="POST" action="/coupon" style="display:flex;gap:8px;margin-top:10px"><input name="coupon" placeholder="GARIA10 / FIRST20 / PUJA50" value="{get_coupon()}" style="flex:1"><button style="background:#8B1E1E;color:#fff;padding:12px 18px;border:none;border-radius:10px;font-weight:800">Apply</button></form>
        <p style="margin-top:8px;font-size:13px;color:#666">{coupon_msg}<br>Try: <b>GARIA10</b> = 10% OFF, <b>FIRST20</b> = 20% OFF, <b>PUJA50</b> = ₹50 OFF</p>
        <hr style="margin:14px 0"><h3>💳 Payment Option - Checkout e pabe</h3><p style="font-size:14px;line-height:1.7;margin-top:8px">1. <b>Cash on Delivery</b> - Delivery te cash<br>2. <b>UPI</b> - GPay / PhonePe - QR scan<br>3. <b>Card</b> - Debit / Credit - Razorpay</p>
      </div>
      <div style="background:#fff;padding:20px;border-radius:16px">
        <div style="display:flex;justify-content:space-between"><span>Subtotal</span><b>₹{sub}</b></div>
        <div style="display:flex;justify-content:space-between;margin-top:8px;color:green"><span>Coupon Discount {f'({get_coupon()})' if get_coupon() else ''}</span><b>- ₹{disc}</b></div>
        <div style="display:flex;justify-content:space-between;margin-top:8px"><span>Delivery</span><b>{'FREE' if fee==0 else f'₹{fee}'}</b></div><hr style="margin:12px 0">
        <div style="display:flex;justify-content:space-between;font-size:20px"><span>Total to Pay</span><b style="color:#8B1E1E">₹{grand}</b></div>
        <a href="/checkout" style="background:#1A7A2E;color:#fff;padding:14px;border:none;border-radius:25px;font-weight:800;display:block;text-align:center;margin-top:14px">Checkout → Payment Koro</a>
        <a href="/" style="display:block;text-align:center;margin-top:10px;color:#888">← Aro Add Koro</a>
      </div>
    </div></section>"""
    return render_page("Cart", content)

# ============================================================
# 7. CHECKOUT + PAYMENT - 3 ta option
# ============================================================
@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    cart = get_cart()
    if not cart and request.method == "GET": return redirect("/")
    # POST - Checkout form submit - Payment page e jabe
    if request.method == "POST":
        session["customer"] = {
            "name": request.form.get("name", "").strip(),
            "phone": request.form.get("phone", "").strip(),
            "address": request.form.get("address", "").strip(),
            "area": request.form.get("area", "Garia"),
            "note": request.form.get("note", "").strip(),
        }
        session["payment_method"] = request.form.get("payment_method", "cod")
        return redirect("/payment")
    sub = cart_subtotal(); disc = coupon_discount(sub); fee = delivery_fee(sub - disc); grand = sub - disc + fee
    items_html = "<br>".join([f"• {PRODUCTS[pid]['name']} - {qty} x ₹{PRODUCTS[pid]['price']} = ₹{PRODUCTS[pid]['price']*qty}" for pid, qty in cart.items()])
    content = f"""
    <section class="section"><h2>Checkout - Step 1: Address + Payment Method</h2>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;align-items:start">
      <form method="POST" class="form-box">
        <h3>📍 Tomar Details</h3>
        <input name="name" placeholder="Tomar Naam *" required>
        <input name="phone" placeholder="Phone Number * - 10 digit" required pattern="[0-9+ ]{{10,13}}">
        <textarea name="address" placeholder="Full Address * - Bari / Flat, Rasta, Landmark" required rows="2"></textarea>
        <select name="area"><option>Garia</option><option>Patuli</option><option>Narendrapur</option><option>Baghajatin</option><option>Bansdroni</option><option>Onno</option></select>
        <input name="note" placeholder="Note - Kom misti / Gorom chai / etc. (Optional)">
        <h3 style="margin-top:6px">💳 Payment Method - Ekta becho</h3>
        <label class="pay-option selected"><input type="radio" name="payment_method" value="cod" checked><div><b>💵 Cash on Delivery (COD)</b><small>Delivery te cash debe - Sobcheye soja - Garia te sobai etai kore</small></div></label>
        <label class="pay-option"><input type="radio" name="payment_method" value="upi"><div><b>📱 UPI - GPay / PhonePe / Paytm</b><small>QR scan kore pay koro - UPI ID: {UPI_ID} - 1 min e</small></div></label>
        <label class="pay-option"><input type="radio" name="payment_method" value="card"><div><b>💳 Card - Debit / Credit / NetBanking</b><small>Razorpay diye secure payment - Card, UPI, NetBanking - Sob cholbe {'(Chalu korte Razorpay key lagbe)' if not RAZORPAY_ENABLED else ''}</small></div></label>
        <button style="background:#1A7A2E;color:#fff;padding:14px;border:none;border-radius:25px;font-weight:800;cursor:pointer">Continue to Payment → ₹{grand}</button>
        <small style="color:#888">Next page e payment confirm korbe - Taka age katbe na - Confirm korlei order jabe.</small>
      </form>
      <div style="background:#fff;padding:20px;border-radius:16px"><h3>Order Summary</h3><p style="margin:12px 0;line-height:1.8">{items_html}</p><hr>
      <p style="margin-top:10px">Subtotal: ₹{sub}<br>Coupon: - ₹{disc} {f'({get_coupon()})' if get_coupon() else ''}<br>Delivery: {'FREE' if fee==0 else f'₹{fee}'}<br><b style="font-size:20px;color:#8B1E1E">Total: ₹{grand}</b></p></div>
    </div></section>
    <script>
      document.querySelectorAll('.pay-option').forEach(el=>{{el.addEventListener('click',()=>{{document.querySelectorAll('.pay-option').forEach(x=>x.classList.remove('selected')); el.classList.add('selected'); el.querySelector('input').checked=true;}})}});
    </script>"""
    return render_page("Checkout", content)

@app.route("/payment", methods=["GET", "POST"])
def payment_page():
    cart = get_cart()
    cust = session.get("customer", {})
    method = session.get("payment_method", "cod")
    if not cart: return redirect("/")
    sub = cart_subtotal(); disc = coupon_discount(sub); fee = delivery_fee(sub - disc); grand = sub - disc + fee
    order_id = session.get("order_id") or gen_order_id()
    session["order_id"] = order_id
    upi_link = make_upi_link(grand, order_id)

    # POST - Payment Confirm - Order save + Success page
    if request.method == "POST":
        txn_id = request.form.get("txn_id", "").strip() or request.form.get("razorpay_payment_id", "").strip() or ("COD-" + order_id)
        upi_ref = request.form.get("upi_ref", "").strip()
        payment_status = "PENDING"
        if method == "cod": payment_status = "COD - Delivery te Cash Debe"
        elif method == "upi": payment_status = f"UPI - Paid - Ref: {upi_ref or txn_id}"
        elif method == "card": payment_status = f"Card - Razorpay - Payment ID: {txn_id}"
        order = {
            "order_id": order_id, "date": datetime.now().strftime("%d %b %Y, %I:%M %p"),
            "customer": cust, "items": [{"name": PRODUCTS[pid]["name"], "qty": qty, "price": PRODUCTS[pid]["price"], "total": PRODUCTS[pid]["price"]*qty} for pid, qty in cart.items()],
            "subtotal": sub, "coupon": get_coupon(), "discount": disc, "delivery": fee, "total": grand,
            "payment_method": method, "payment_status": payment_status, "txn_id": txn_id or upi_ref,
            "status": "CONFIRMED - Banano Hocche"
        }
        save_order(order)
        # WhatsApp message
        lines = [f"Hi {SHOP_NAME}! Notun Order 🍯 - {order_id}", f"Naam: {cust.get('name')}", f"Phone: {cust.get('phone')}", f"Address: {cust.get('address')}, {cust.get('area')}", f"Payment: {method.upper()} - {payment_status}", "--- Order ---"]
        for it in order["items"]: lines.append(f"• {it['name']} - {it['qty']} x ₹{it['price']} = ₹{it['total']}")
        lines += [f"Subtotal: ₹{sub}", f"Discount: -₹{disc}", f"Delivery: {'FREE' if fee==0 else f'₹{fee}'}", f"TOTAL PAID / TO PAY: ₹{grand}"]
        if cust.get("note"): lines.append(f"Note: {cust.get('note')}")
        wa_msg = "\n".join(lines)
        session["last_order"] = order
        session["cart"] = {}; session["coupon"] = ""; session.pop("order_id", None)
        # Success page e WhatsApp link diye
        wa_link = f"https://wa.me/{WHATSAPP}?text={urllib.parse.quote(wa_msg)}"
        content = f"""
        <section class="section"><div class="success">
          <h2 style="color:#1A7A2E;font-size:32px">✅ Order Confirm Hoyeche!</h2>
          <p style="margin:14px 0;font-size:18px">Order ID: <b>{order_id}</b><br>Total: <b>₹{grand}</b> - Payment: <b>{method.upper()}</b><br>Status: {payment_status}</p>
          <p>Amra 5 min e call kore confirm korbo. Delivery 1 ghontay - Garia te.</p>
          <p style="margin-top:16px;display:flex;gap:10px;justify-content:center;flex-wrap:wrap">
            <a href="{wa_link}" target="_blank" style="background:#25D366;color:#fff;padding:13px 20px;border-radius:25px;font-weight:800;display:inline-block">💬 WhatsApp e Order Pathao</a>
            <a href="/orders" style="background:#fff;border:2px solid #8B1E1E;color:#8B1E1E;padding:11px 18px;border-radius:25px;font-weight:800;display:inline-block">📋 My Orders Dekho</a>
            <a href="/" style="background:#8B1E1E;color:#fff;padding:13px 20px;border-radius:25px;font-weight:800;display:inline-block">← Aro Order Koro</a>
          </p>
          <p style="margin-top:12px;font-size:13px;color:#666">Order ta <b>orders.txt / orders.json</b> e save hoye geche - Admin e dekhte parbe.</p>
        </div></section>"""
        return render_page("Order Success", content)

    # GET - Payment Page - Method onujayi alada UI
    items_html = "<br>".join([f"• {PRODUCTS[pid]['name']} - {qty} x ₹{PRODUCTS[pid]['price']} = ₹{PRODUCTS[pid]['price']*qty}" for pid, qty in cart.items()])
    if method == "cod":
        pay_html = f"""
        <div style="background:#FFF7EB;padding:20px;border-radius:14px;text-align:center">
          <h3 style="font-size:28px">💵 Cash on Delivery</h3><p style="margin:10px 0;line-height:1.6">Delivery boy jokhon misti debe - Tokhon <b>₹{grand} cash</b> debe.<br>Ekhon kono taka dite hobe na - Sudhu Confirm koro.</p>
          <form method="POST"><button style="background:#1A7A2E;color:#fff;padding:14px 28px;border:none;border-radius:25px;font-weight:800;cursor:pointer;font-size:16px">✅ Confirm Order - COD - ₹{grand}</button></form>
        </div>"""
    elif method == "upi":
        # QR Image - Google Chart API diye UPI QR banano - No extra library lagbe na
        qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=220x220&data={urllib.parse.quote(upi_link)}"
        pay_html = f"""
        <div class="upi-box">
          <h3>📱 UPI Payment - GPay / PhonePe / Paytm</h3>
          <p style="margin:10px 0">Nicher QR ta <b>GPay / PhonePe</b> diye scan koro - <b>₹{grand}</b> pay koro</p>
          <img src="{qr_url}" alt="UPI QR" style="width:220px;height:220px;border:4px solid #fff;box-shadow:0 4px 16px rgba(0,0,0,.1);border-radius:12px">
          <p style="margin:10px 0"><b>UPI ID:</b> {UPI_ID}<br><b>Naam:</b> {UPI_NAME}<br><b>Amount:</b> ₹{grand} - <b>Order ID:</b> {order_id}</p>
          <p><a href="{upi_link}" style="background:#1A7A2E;color:#fff;padding:11px 18px;border-radius:25px;font-weight:800;display:inline-block">📱 Mobile e - GPay / PhonePe Kholo → Pay ₹{grand}</a></p>
          <p style="font-size:13px;color:#666;margin-top:8px">Desktop e thakle - Mobile diye QR scan koro. Pay hoye gele - Nicher box e UTR / Ref No. dao.</p>
          <form method="POST" style="display:grid;gap:10px;max-width:400px;margin:14px auto 0;text-align:left">
            <input name="upi_ref" placeholder="UTR / UPI Ref No. - Jemon: 412345678901 (GPay te pabe) *" required>
            <input name="txn_id" placeholder="Tomar Naam - Jeta diye pay korle (Optional)">
            <button style="background:#1A7A2E;color:#fff;padding:13px;border:none;border-radius:25px;font-weight:800;cursor:pointer">✅ Payment Done - Order Confirm Koro</button>
          </form>
          <p style="margin-top:10px;font-size:13px">Pay na koreo - <a href="/payment" onclick="document.querySelector('form').submit();return false" style="color:#8B1E1E;font-weight:700">COD te bodlao</a> - Ba <a href="/checkout" style="color:#8B1E1E">← Back</a></p>
        </div>"""
    else:  # card - Razorpay
        if RAZORPAY_ENABLED:
            pay_html = f"""
            <div style="background:#fff;padding:20px;border-radius:14px;text-align:center;border:2px solid #2A6DF4">
              <h3>💳 Card / UPI / NetBanking - Razorpay Secure</h3><p style="margin:10px 0">Razorpay popup khulbe - Card / UPI / NetBanking diye <b>₹{grand}</b> pay koro.</p>
              <button id="rzp-btn" style="background:#2A6DF4;color:#fff;padding:14px 28px;border:none;border-radius:25px;font-weight:800;cursor:pointer;font-size:16px">💳 Pay ₹{grand} - Razorpay</button>
              <form method="POST" id="rzp-form" style="display:none"><input name="razorpay_payment_id" id="rzp-pid"><input name="txn_id" id="rzp-txn"></form>
              <p style="font-size:12px;color:#888;margin-top:10px">Razorpay - PCI DSS Secure - Card details amader kache ase na.</p>
            </div>
            <script>
              var options = {{"key": "{RAZORPAY_KEY_ID}", "amount": {grand*100}, "currency": "INR", "name": "{SHOP_NAME}", "description": "Order {order_id}", "order_id": "", "prefill": {{"name": "{cust.get('name','')}", "contact": "{cust.get('phone','')}"}}, "theme": {{"color": "#8B1E1E"}},
              "handler": function(res){{ document.getElementById('rzp-pid').value = res.razorpay_payment_id; document.getElementById('rzp-txn').value = res.razorpay_payment_id; document.getElementById('rzp-form').submit(); }},
              "modal": {{"ondismiss": function(){{ alert('Payment cancel korle - Order confirm hobe na. COD bechte paro.'); }}}};
              document.getElementById('rzp-btn').onclick = function(e){{ var rzp = new Razorpay(options); rzp.open(); e.preventDefault(); }};
            </script>"""
        else:
            pay_html = f"""
            <div style="background:#FFF3CD;padding:20px;border-radius:14px;text-align:center">
              <h3>💳 Card Payment - Ekhono Setup Hoyni</h3>
              <p style="margin:10px 0;line-height:1.7">Card payment chalu korte - Razorpay account lagbe - 10 min e free te khola jay.<br>Ekhon - <b>UPI</b> ba <b>COD</b> diye order koro - Oi 2 to chalu ache.</p>
              <p style="display:flex;gap:10px;justify-content:center;flex-wrap:wrap"><a href="/checkout" style="background:#1A7A2E;color:#fff;padding:12px 18px;border-radius:25px;font-weight:800;display:inline-block">← UPI / COD Becho</a>
              <a href="https://razorpay.com" target="_blank" style="background:#fff;border:2px solid #8B1E1E;color:#8B1E1E;padding:10px 16px;border-radius:25px;font-weight:800;display:inline-block">Razorpay Account Kholo →</a></p>
              <form method="POST" style="margin-top:14px"><input type="hidden" name="txn_id" value="CARD-NOT-SETUP-{order_id}"><button style="background:#8B1E1E;color:#fff;padding:12px 22px;border:none;border-radius:25px;font-weight:800;cursor:pointer">COD diye Order Koro - ₹{grand}</button></form>
            </div>"""
    content = f"""
    <section class="section"><h2>Payment - Step 2: Pay Koro - Order ID: {order_id}</h2>
    <p style="margin-top:6px">Naam: <b>{cust.get('name')}</b> | Phone: <b>{cust.get('phone')}</b> | Address: {cust.get('address')}, {cust.get('area')} | Method: <b>{method.upper()}</b></p>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:16px;align-items:start">
      <div style="background:#fff;padding:20px;border-radius:16px">{pay_html}<p style="margin-top:12px;text-align:center"><a href="/checkout" style="color:#8B1E1E">← Payment Method Bodlao</a> • <a href="/cart" style="color:#8B1E1E">Cart</a></p></div>
      <div style="background:#fff;padding:20px;border-radius:16px"><h3>Order Summary</h3><p style="margin:12px 0;line-height:1.8">{items_html}</p><hr>
      <p style="margin-top:10px">Subtotal: ₹{sub}<br>Coupon: - ₹{disc}<br>Delivery: {'FREE' if fee==0 else f'₹{fee}'}<br><b style="font-size:20px;color:#8B1E1E">Total to Pay: ₹{grand}</b></p>
      <p style="margin-top:12px;font-size:13px;color:#666">🔒 Payment secure. COD hole - Delivery te cash. UPI hole - UTR dao. Card hole - Razorpay popup.</p></div>
    </div></section>"""
    return render_page("Payment", content)

# ============================================================
# 8. ORDERS + ADMIN + API
# ============================================================
@app.route("/orders")
def orders_page():
    orders = get_orders()
    if not orders:
        return render_page("Orders", """<section class="section"><h2>📋 My Orders</h2><p style="margin-top:10px">Ekhono kono order nei.</p><p style="margin-top:12px"><a href="/" style="background:#8B1E1E;color:#fff;padding:12px 18px;border-radius:25px;font-weight:800;display:inline-block">← Order Koro</a></p></section>""")
    html = ""
    for o in orders[:20]:
        items = "<br>".join([f"• {it['name']} - {it['qty']} x ₹{it['price']} = ₹{it['total']}" for it in o["items"]])
        html += f"""<div style="background:#fff;padding:18px;border-radius:16px;margin-top:12px"><b>Order {o['order_id']}</b> - {o['date']} - <span style="color:green">{o['status']}</span><br>
        {o['customer'].get('name')} - {o['customer'].get('phone')} - {o['customer'].get('address')}, {o['customer'].get('area')}<br>
        <p style="margin:8px 0;line-height:1.7">{items}</p><b>Total: ₹{o['total']}</b> - Payment: {o['payment_method'].upper()} - {o['payment_status']}</div>"""
    return render_page("Orders", f"""<section class="section"><h2>📋 All Orders - {len(orders)} ta</h2>{html}</section>""")

@app.route("/about")
def about(): return render_page("Our Story", """<section class="section"><h2>Our Story - 1995 Theke Garia Te</h2><p style="margin-top:12px;line-height:1.8">1995 e Garia Station Road e suru. Protidin sokal 6 ta te banano - Ek i taste.</p></section>""")
@app.route("/faq")
def faq(): return render_page("FAQ", """<section class="section"><h2>FAQ - Payment</h2><div style="background:#fff;padding:20px;border-radius:16px;margin-top:14px;line-height:2"><b>COD ache?</b> - Ha, delivery te cash.<br><b>UPI te ki kore pay korbo?</b> - QR scan koro - GPay / PhonePe.<br><b>Card payment?</b> - Razorpay diye - Debit / Credit.<br><b>Payment fail hole?</b> - Taka katle 3-5 din e refund - WhatsApp koro.<br><b>Advance lagbe?</b> - Biyer order e 50% advance.</div></section>""")
@app.route("/contact")
def contact(): return render_page("Contact", f"""<section class="section"><h2>Contact</h2><div style="background:#fff;padding:20px;border-radius:16px;margin-top:14px;line-height:1.8">📍 {SHOP_ADDRESS}<br>📞 WhatsApp: {WHATSAPP}<br>💳 UPI: {UPI_ID}<br>⏰ {SHOP_TIME}</div></section>""")

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        if request.form.get("password") != "garia123":
            return render_page("Admin", """<section class="section"><h2>Wrong Password</h2><p><a href="/admin">← Try Again</a></p></section>""")
        for pid in PRODUCTS:
            val = request.form.get(f"price_{pid}")
            if val and val.isdigit(): PRODUCTS[pid]["price"] = int(val)
        return redirect("/admin?saved=1")
    saved = request.args.get("saved")
    rows = "".join([f"""<tr><td>{p['emoji']} {p['name']}</td><td><input name="price_{pid}" value="{p['price']}" style="width:90px"></td><td>₹{p['price']}</td></tr>""" for pid, p in PRODUCTS.items()])
    orders = get_orders()
    ord_html = "".join([f"""<div style="background:#F9F9F9;padding:12px;border-radius:10px;margin-top:8px"><b>{o['order_id']}</b> - ₹{o['total']} - {o['payment_method'].upper()} - {o['payment_status']} - {o['customer'].get('name')} - {o['customer'].get('phone')}</div>""" for o in orders[:10]]) or "Kono order nei."
    content = f"""<section class="section"><h2>Admin - Dam + Orders + Payment</h2><p>Password: <b>garia123</b> {'<b style="color:green">✅ Saved!</b>' if saved else ''}</p>
    <form method="POST" style="background:#fff;padding:20px;border-radius:16px;margin-top:14px"><input type="password" name="password" placeholder="Password - garia123" required style="max-width:300px;margin-bottom:14px">
    <table><tr><th>Misti</th><th>Notun Dam</th><th>Ekhon</th></tr>{rows}</table>
    <button style="background:#8B1E1E;color:#fff;padding:13px 24px;border:none;border-radius:25px;font-weight:800;margin-top:14px;cursor:pointer">Save Dam →</button></form>
    <h3 style="margin-top:22px">📋 Last 10 Orders - Payment Status</h3><div style="background:#fff;padding:16px;border-radius:16px;margin-top:10px">{ord_html}</div>
    <p style="margin-top:12px">Payment Config: UPI ID = <b>{UPI_ID}</b> | Razorpay Enabled = <b>{RAZORPAY_ENABLED}</b> | COD = Always ON</p></section>"""
    return render_page("Admin", content)

# Razorpay Verify - Jodi Razorpay use koro - Frontend theke payment_id asle - Ekhane verify korbe
@app.route("/api/verify-payment", methods=["POST"])
def verify_payment():
    data = request.get_json() or {}
    # Real verify: hmac.new(RAZORPAY_KEY_SECRET.encode(), f"{data.get('order_id')}|{data.get('payment_id')}".encode(), hashlib.sha256).hexdigest()
    # Ekhon demo - Shudhu payment_id thaklei OK
    if data.get("payment_id"):
        return jsonify({"success": True, "message": "Payment verified"})
    return jsonify({"success": False, "message": "Payment ID nei"}), 400

@app.route("/api/menu")
def api_menu(): return jsonify({"shop": SHOP_NAME, "menu": MENU, "products": PRODUCTS, "upi_id": UPI_ID, "whatsapp": WHATSAPP})

import os
if __name__ == "__main__":
    port=int(os.environ.get ( "PORT", 5000))
    print("\n✅ Garia Misthanna Bhandar - Menu + Ordering + Payment - Cholche!")
    print("👉 Home: http://127.0.0.1:5000")
    print("🛒 Cart: http://127.0.0.1:5000/cart")
    print("💳 Checkout + Payment: http://127.0.0.1:5000/checkout")
    print("📋 Orders: http://127.0.0.1:5000/orders")
    print("🔧 Admin: http://127.0.0.1:5000/admin - Password: garia123")
    print("💡 UPI ID ekhono demo - Upor e UPI_ID bodlao - Nahole taka onno jaygay jabe na, test e thakbe\n")
    app.run(host ="0.0.0.0",port=port,debug=False)