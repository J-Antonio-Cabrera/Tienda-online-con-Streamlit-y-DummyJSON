import requests
import streamlit as st
from datetime import datetime, timedelta
import random

def h(content):
    return " ".join(content.split())

st.set_page_config(
    page_title="NovaShop | Tu tienda online",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

defaults = {
    "page": "home", "carrito": {}, "wishlist": set(),
    "recently_viewed": [], "selected_product": None,
    "selected_image_index": 0, "coupon": None, "order": None,
    "user": {"nombre": "Invitado", "logged": False},
    "grupo_sel": "Todas",
    "cat_especifica": "Todas",
    "marca_sel": "Todas",
    "rating_min": 0,
    "solo_ofertas_chk": False,
    "solo_stock_chk": True,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

CUPONES = {
    "NOVA10": {"desc": 10, "min": 0, "tipo": "porcentaje"},
    "NOVA20": {"desc": 20, "min": 100, "tipo": "porcentaje"},
    "BIENVENIDO": {"desc": 5, "min": 0, "tipo": "porcentaje"},
    "ENVIOGRATIS": {"desc": 0, "min": 0, "tipo": "envio_gratis"},
}
ENVIO_BASE = 99.0
ENVIO_GRATIS_DESDE = 500.0
IVA = 0.16

CATEGORIAS_ES = {
    "beauty": "Belleza", "fragrances": "Fragancias", "furniture": "Muebles",
    "groceries": "Abarrotes", "home-decoration": "Decoración",
    "kitchen-accessories": "Cocina", "laptops": "Laptops",
    "mens-shirts": "Camisas Hombre", "mens-shoes": "Zapatos Hombre",
    "mens-watches": "Relojes Hombre", "mobile-accessories": "Acc. Móviles",
    "motorcycle": "Motocicletas", "skin-care": "Cuidado Piel",
    "smartphones": "Smartphones", "sports-accessories": "Deportes",
    "sunglasses": "Gafas de Sol", "tablets": "Tablets", "tops": "Blusas",
    "vehicle": "Vehículos", "womens-bags": "Bolsos Mujer",
    "womens-dresses": "Vestidos Mujer", "womens-jewellery": "Joyería Mujer",
    "womens-shoes": "Zapatos Mujer", "womens-watches": "Relojes Mujer",
}

GRUPOS_FILTRO = {
    "Todas": None,
    "👩 Mujer": ["womens-dresses", "womens-shoes", "womens-bags", "womens-jewellery", "womens-watches"],
    "👨 Hombre": ["mens-shirts", "mens-shoes", "mens-watches"],
    "💄 Belleza": ["beauty", "fragrances", "skin-care"],
    "📱 Tecnología": ["smartphones", "laptops", "tablets", "mobile-accessories"],
    "🏠 Hogar": ["furniture", "home-decoration", "kitchen-accessories"],
    "🔥 Ofertas": "OFERTAS",
}

def cat_es(cat):
    return CATEGORIAS_ES.get(cat, cat.title())

st.markdown(h("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

    #MainMenu, footer, header {visibility: hidden;}
    [data-testid="stHeader"] {display: none !important;}
    .block-container {padding-top: 0 !important; padding-bottom: 2rem; max-width: 1400px;}
    section.main > div { padding-top: 0 !important; }

    .stApp { background: #FFFFFF; font-family: 'Inter', sans-serif; }
    [data-testid="stAppViewContainer"] { background: #FFFFFF; }

    [data-testid="stSidebar"] {
        display: block !important;
        visibility: visible !important;
        opacity: 1 !important;
        transform: none !important;
        margin-left: 0 !important;
        left: 0 !important;
        width: 320px !important;
        min-width: 320px !important;
        max-width: 320px !important;
        background: #FFFFFF !important;
        border-right: 1px solid #E5E7EB !important;
    }

    [data-testid="stSidebar"][aria-expanded="false"] {
        display: block !important;
        visibility: visible !important;
        transform: none !important;
        width: 320px !important;
        min-width: 320px !important;
    }

    [data-testid="stSidebar"] > div:first-child {
        width: 320px !important;
        padding: 24px 20px !important;
    }

    [data-testid="collapsedControl"] {
        display: none !important;
    }

    .utility-bar {
        display: flex;
        justify-content: flex-end;
        gap: 22px;
        padding: 10px 0 6px;
        font-size: 12px;
        color: #6B7280;
        border-bottom: 1px solid #F3F4F6;
        margin-bottom: 4px;
    }
    .utility-bar a {
        color: #6B7280;
        text-decoration: none;
        transition: color 0.15s;
    }
    .utility-bar a:hover { color: #111827; }

    .brand-logo {
        font-family: 'Inter', sans-serif;
        font-size: 30px;
        font-weight: 900;
        letter-spacing: -1.5px;
        color: #111827;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .brand-logo .accent { color: #3483FA; }
    .brand-mark {
        width: 34px;
        height: 34px;
        background: #111827;
        color: white;
        border-radius: 4px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
    }

    .nav-buttons .stButton > button {
        background: transparent !important;
        border: none !important;
        color: #111827 !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        padding: 10px 6px !important;
        border-radius: 0 !important;
        border-bottom: 2px solid transparent !important;
        transition: all 0.15s !important;
    }
    .nav-buttons .stButton > button:hover {
        color: #3483FA !important;
        border-bottom-color: #3483FA !important;
        background: transparent !important;
    }
    .nav-buttons .stButton > button:focus {
        color: #3483FA !important;
        border-bottom-color: #3483FA !important;
        box-shadow: none !important;
    }

    .icon-buttons .stButton > button {
        background: transparent !important;
        border: 1px solid #E5E7EB !important;
        color: #111827 !important;
        border-radius: 50% !important;
        width: 44px !important;
        height: 44px !important;
        padding: 0 !important;
        font-size: 17px !important;
        font-weight: 600 !important;
        min-width: 44px !important;
    }
    .icon-buttons .stButton > button:hover {
        border-color: #111827 !important;
        background: #F9FAFB !important;
    }

    .promo-banner {
        background: linear-gradient(90deg, #EEF2FF 0%, #F5F3FF 50%, #FDF2F8 100%);
        padding: 14px 0;
        text-align: center;
        font-size: 14px;
        font-weight: 600;
        color: #111827;
        margin-bottom: 20px;
        position: relative;
        border-radius: 4px;
    }
    .promo-banner .arrow {
        position: absolute;
        right: 30px;
        top: 50%;
        transform: translateY(-50%);
        font-size: 20px;
        color: #111827;
    }
    .promo-banner b { font-weight: 800; }

    .hero-grid {
        display: grid;
        grid-template-columns: 1fr 2fr;
        gap: 8px;
        margin-bottom: 30px;
    }
    .hero-black {
        background: #111827;
        color: white;
        padding: 40px 32px;
        border-radius: 4px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        min-height: 360px;
    }
    .hero-black-title {
        font-size: 34px;
        font-weight: 900;
        line-height: 1.05;
        letter-spacing: -1px;
        margin: 0 0 16px 0;
        text-transform: uppercase;
    }
    .hero-black-sub {
        font-size: 14px;
        line-height: 1.5;
        opacity: 0.85;
        margin-bottom: 24px;
    }
    .hero-black-btn {
        background: white;
        color: #111827;
        padding: 12px 24px;
        font-weight: 800;
        font-size: 13px;
        letter-spacing: 0.5px;
        display: inline-block;
        border-radius: 2px;
        width: fit-content;
        text-transform: uppercase;
    }

    .hero-cats { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; }
    .hero-cat {
        background: #F5F5F5;
        border-radius: 4px;
        min-height: 360px;
        position: relative;
        overflow: hidden;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        padding: 20px;
    }
    .hero-cat img {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        max-width: 80%;
        max-height: 60%;
        object-fit: contain;
    }
    .hero-cat-label {
        background: white;
        color: #111827;
        padding: 8px 16px;
        font-weight: 800;
        font-size: 12px;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        width: fit-content;
        border-radius: 2px;
        display: flex;
        align-items: center;
        gap: 6px;
        z-index: 2;
        position: relative;
    }
    .hero-cat-label::before {
        content: "%";
        color: #E11D48;
        font-weight: 900;
    }

    .stButton > button {
        background: #FFFFFF !important;
        color: #111827 !important;
        border: 1px solid #E5E7EB !important;
        padding: 10px 16px !important;
        border-radius: 4px !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        transition: all 0.15s !important;
    }
    .stButton > button:hover {
        background: #F9FAFB !important;
        border-color: #111827 !important;
        color: #111827 !important;
    }
    .stButton > button[kind="primary"] {
        background: #111827 !important;
        color: white !important;
        border: 1px solid #111827 !important;
    }
    .stButton > button[kind="primary"]:hover {
        background: #374151 !important;
        color: white !important;
    }
    [data-testid="stFormSubmitButton"] button {
        background: #111827 !important;
        color: white !important;
        border: none !important;
        font-weight: 700 !important;
        padding: 14px 20px !important;
        border-radius: 4px !important;
        font-size: 15px !important;
    }
    [data-testid="stFormSubmitButton"] button:hover {
        background: #374151 !important;
        color: white !important;
    }

    [data-testid="stForm"] {
        background: white !important;
        padding: 24px !important;
        border-radius: 8px !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
        border: 1px solid #F3F4F6 !important;
    }

    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stTextArea textarea,
    .stSelectbox > div > div > div {
        background: #FFFFFF !important;
        border: 1px solid #D1D5DB !important;
        border-radius: 4px !important;
        color: #111827 !important;
        font-size: 14px !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #111827 !important;
        box-shadow: 0 0 0 3px rgba(17,24,39,0.08) !important;
    }
    .stTextInput label, .stNumberInput label, .stSelectbox label, .stRadio label {
        color: #374151 !important;
        font-size: 13px !important;
        font-weight: 600 !important;
    }
    .stRadio > div > label { color: #374151 !important; font-size: 14px !important; }

    .ml-card {
        background: white;
        border-radius: 6px;
        padding: 16px;
        box-shadow: 0 0 0 1px #F3F4F6;
        transition: all 0.2s;
        position: relative;
        height: 400px;
        display: flex;
        flex-direction: column;
    }
    .ml-card:hover { box-shadow: 0 0 0 1px #111827, 0 4px 16px rgba(0,0,0,0.06); }
    .ml-img-box { height: 170px; display: flex; align-items: center; justify-content: center; margin-bottom: 10px; overflow: hidden; }
    .ml-img-box img { max-height: 100%; max-width: 100%; object-fit: contain; transition: transform 0.3s; }
    .ml-card:hover .ml-img-box img { transform: scale(1.06); }

    .ml-title {
        font-size: 14px; font-weight: 500; color: #111827;
        line-height: 1.35; height: 38px; overflow: hidden;
        display: -webkit-box; -webkit-line-clamp: 2;
        -webkit-box-orient: vertical; margin: 8px 0;
    }
    .ml-price-row { display: flex; align-items: baseline; gap: 8px; margin-bottom: 2px; }
    .ml-price { font-size: 20px; font-weight: 800; color: #111827; letter-spacing: -0.5px; }
    .ml-discount { font-size: 13px; font-weight: 700; color: #E11D48; }
    .ml-old-price { font-size: 12px; color: #9CA3AF; text-decoration: line-through; }
    .ml-shipping { color: #059669; font-size: 12px; font-weight: 700; margin-top: 4px; }
    .ml-full-badge { background: #111827; color: white; font-size: 9px; padding: 2px 6px; border-radius: 2px; font-weight: 800; margin-left: 4px; letter-spacing: 0.5px; }
    .ml-rating-row { display: flex; align-items: center; gap: 6px; font-size: 12px; color: #6B7280; margin-top: 6px; }
    .ml-stars-gold { color: #FFB400; font-size: 14px; letter-spacing: 1px; }
    .ml-rating-num { color: #6B7280; font-size: 12px; font-weight: 600; }
    .ml-tag-off { position: absolute; top: 12px; right: 12px; background: #E11D48; color: white; padding: 3px 8px; border-radius: 2px; font-size: 11px; font-weight: 800; z-index: 5; }
    .ml-tag-new { position: absolute; top: 12px; left: 12px; background: #111827; color: white; padding: 3px 8px; border-radius: 2px; font-size: 10px; font-weight: 800; letter-spacing: 0.5px; z-index: 5; }

    .ml-section-title { font-size: 24px; font-weight: 900; color: #111827; letter-spacing: -0.5px; margin: 32px 0 16px; }

    .ml-detail-card { background: white; border-radius: 6px; padding: 24px; box-shadow: 0 0 0 1px #F3F4F6; }
    .ml-detail-title { font-size: 26px; font-weight: 800; color: #111827; line-height: 1.25; letter-spacing: -0.5px; margin-bottom: 8px; }
    .ml-detail-meta { font-size: 12px; color: #9CA3AF; margin-bottom: 12px; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600; }
    .ml-detail-price { font-size: 34px; font-weight: 800; color: #111827; margin: 8px 0; letter-spacing: -1px; }
    .ml-detail-discount { font-size: 16px; color: #E11D48; font-weight: 700; margin-left: 12px; }
    .ml-detail-old { font-size: 14px; color: #9CA3AF; text-decoration: line-through; }
    .ml-detail-shipping { color: #059669; font-weight: 700; font-size: 15px; margin: 16px 0; }
    .ml-stock-good { background: #ECFDF5; color: #059669; padding: 12px 16px; border-radius: 4px; font-weight: 700; font-size: 13px; margin: 16px 0; }
    .ml-stock-low { background: #FFF7ED; color: #C2410C; padding: 12px 16px; border-radius: 4px; font-weight: 700; font-size: 13px; margin: 16px 0; }
    .ml-stock-out { background: #FEF2F2; color: #DC2626; padding: 12px 16px; border-radius: 4px; font-weight: 700; font-size: 13px; margin: 16px 0; }
    .ml-feature-item { display: flex; gap: 10px; padding: 8px 0; font-size: 13px; color: #4B5563; }
    .ml-stars-big { color: #FFB400; font-size: 18px; letter-spacing: 2px; }

    .ml-cart-img { width: 80px; height: 80px; background: #F9FAFB; border-radius: 4px; display: flex; align-items: center; justify-content: center; padding: 6px; }
    .ml-cart-img img { max-height: 100%; max-width: 100%; object-fit: contain; }
    .ml-summary { background: white; border-radius: 6px; padding: 24px; box-shadow: 0 0 0 1px #F3F4F6; }
    .ml-summary-row { display: flex; justify-content: space-between; font-size: 14px; color: #6B7280; margin-bottom: 10px; }
    .ml-summary-total { display: flex; justify-content: space-between; font-size: 22px; font-weight: 900; color: #111827; padding-top: 14px; border-top: 1px solid #F3F4F6; margin-top: 14px; letter-spacing: -0.5px; }
    .ml-free-shipping { background: #ECFDF5; color: #059669; padding: 10px 14px; border-radius: 4px; font-size: 13px; font-weight: 600; margin-top: 12px; }

    .ml-steps { background: white; padding: 18px 24px; border-radius: 6px; display: flex; gap: 20px; margin-bottom: 24px; box-shadow: 0 0 0 1px #F3F4F6; }
    .ml-step { display: flex; align-items: center; gap: 8px; color: #9CA3AF; font-size: 14px; font-weight: 500; flex: 1; }
    .ml-step.active { color: #111827; font-weight: 700; }
    .ml-step.done { color: #059669; }
    .ml-step-num { width: 28px; height: 28px; border-radius: 50%; background: #F3F4F6; color: #9CA3AF; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 13px; }
    .ml-step.active .ml-step-num { background: #111827; color: white; }
    .ml-step.done .ml-step-num { background: #059669; color: white; }

    .ml-success { background: white; border-radius: 6px; padding: 40px 32px; text-align: center; box-shadow: 0 0 0 1px #F3F4F6; margin-bottom: 20px; }
    .ml-success-icon { width: 70px; height: 70px; background: #111827; color: white; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; font-size: 36px; margin-bottom: 16px; }
    .ml-success-title { font-size: 26px; font-weight: 900; color: #111827; margin-bottom: 8px; letter-spacing: -0.5px; }
    .ml-success-sub { color: #6B7280; font-size: 14px; }
    .ml-order-num { background: #F9FAFB; border-radius: 4px; padding: 12px; text-align: center; margin: 16px 0; font-family: monospace; font-size: 16px; font-weight: 700; color: #111827; }

    [data-testid="stSidebar"] * {
        color: #111827;
    }
    [data-testid="stSidebar"] .stMarkdown h1,
    [data-testid="stSidebar"] .stMarkdown h2,
    [data-testid="stSidebar"] .stMarkdown h3,
    [data-testid="stSidebar"] .stMarkdown h4 {
        color: #111827 !important;
        font-weight: 800 !important;
    }
    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] .stMarkdown span {
        color: #374151 !important;
    }
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stSlider label,
    [data-testid="stSidebar"] .stCheckbox label {
        color: #374151 !important;
        font-weight: 700 !important;
        font-size: 14px !important;
    }
    [data-testid="stSidebar"] .stCheckbox > label > div > p,
    [data-testid="stSidebar"] .stCheckbox [data-testid="stMarkdownContainer"] p {
        color: #111827 !important;
        font-weight: 600 !important;
        font-size: 14px !important;
    }
    [data-testid="stSidebar"] .stSlider [data-testid="stTickBarMin"],
    [data-testid="stSidebar"] .stSlider [data-testid="stTickBarMax"],
    [data-testid="stSidebar"] .stSlider [data-baseweb="slider"] div {
        color: #111827 !important;
    }
    [data-testid="stSidebar"] .stSelectbox > div > div > div {
        background: #FFFFFF !important;
        color: #111827 !important;
        border: 1px solid #D1D5DB !important;
    }
    [data-testid="stSidebar"] .stSelectbox svg {
        fill: #111827 !important;
    }
    [data-testid="stSidebar"] .stCaption,
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {
        color: #4B5563 !important;
        font-weight: 600 !important;
    }
    [data-testid="stSidebar"] hr {
        border: none !important;
        border-top: 1px solid #E5E7EB !important;
        margin: 20px 0 !important;
    }
    [data-testid="stSidebar"] .stSelectbox,
    [data-testid="stSidebar"] .stSlider,
    [data-testid="stSidebar"] .stCheckbox,
    [data-testid="stSidebar"] .stSelectSlider {
        margin-bottom: 12px !important;
    }
    [data-testid="stSidebar"] label {
        margin-bottom: 6px !important;
        display: block !important;
    }

    .footer-container {
        background: #111827;
        color: white;
        margin-top: 60px;
        margin-left: -2rem;
        margin-right: -2rem;
        margin-bottom: -2rem;
        padding: 48px 40px 20px;
    }
    .footer-grid {
        display: grid;
        grid-template-columns: 1fr 1fr 1fr 1fr 1.2fr;
        gap: 40px;
        max-width: 1400px;
        margin: 0 auto 40px;
    }
    .footer-col { display: flex; flex-direction: column; gap: 6px; }
    .footer-title {
        color: #FFFFFF;
        font-size: 13px;
        font-weight: 800;
        letter-spacing: 1.5px;
        margin: 0 0 12px 0;
        text-transform: uppercase;
    }
    .footer-col a {
        color: #D1D5DB;
        font-size: 13px;
        text-decoration: none;
        padding: 3px 0;
        transition: color 0.15s;
        font-weight: 400;
    }
    .footer-col a:hover { color: #FFFFFF; text-decoration: underline; }

    .footer-social { align-items: flex-start; }
    .social-icons {
        display: flex;
        gap: 12px;
        margin-bottom: 20px;
        flex-wrap: wrap;
    }
    .social-icons span {
        width: 36px;
        height: 36px;
        background: #1F2937;
        border-radius: 50%;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 16px;
        cursor: pointer;
        transition: all 0.15s;
    }
    .social-icons span:hover { background: #374151; transform: translateY(-2px); }

    .footer-club {
        background: #1F2937;
        border-radius: 8px;
        padding: 14px 16px;
        display: flex;
        align-items: center;
        gap: 12px;
        margin-top: 4px;
    }
    .club-badge { font-size: 24px; }
    .club-text { display: flex; flex-direction: column; }
    .club-text b {
        color: #FFFFFF;
        font-size: 13px;
        font-weight: 800;
        letter-spacing: 0.5px;
    }
    .club-text span { color: #9CA3AF; font-size: 11px; margin-top: 2px; }

    .footer-bottom {
        border-top: 1px solid #374151;
        padding-top: 20px;
        max-width: 1400px;
        margin: 0 auto;
        text-align: center;
    }
    .footer-legal {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 10px;
        flex-wrap: wrap;
        margin-bottom: 12px;
    }
    .footer-legal a {
        color: #D1D5DB;
        font-size: 12px;
        text-decoration: none;
        transition: color 0.15s;
    }
    .footer-legal a:hover { color: #FFFFFF; text-decoration: underline; }
    .footer-legal span { color: #4B5563; font-size: 12px; }

    .footer-copy {
        color: #9CA3AF;
        font-size: 12px;
        font-weight: 400;
        margin-top: 8px;
    }
</style>
"""), unsafe_allow_html=True)


@st.cache_data(ttl=600)
def get_all_products():
    try:
        r = requests.get("https://dummyjson.com/products?limit=194", timeout=15)
        r.raise_for_status()
        return r.json().get("products", [])
    except Exception as e:
        st.error(f"Error API: {e}")
        return []

@st.cache_data(ttl=600)
def get_product_by_id(pid):
    try:
        r = requests.get(f"https://dummyjson.com/products/{pid}", timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None

PRODUCTOS = get_all_products()
if not PRODUCTOS:
    st.stop()


def total_carrito():
    return sum(i["price"] * i["cantidad"] for i in st.session_state.carrito.values())

def cant_carrito():
    return sum(i["cantidad"] for i in st.session_state.carrito.values())

def precio_desc(p):
    desc = p.get("discountPercentage", 0)
    return p["price"], p["price"] / (1 - desc / 100) if desc > 0 else p["price"]

def estrellas_html(rating):
    llenas = int(round(rating))
    return "★" * llenas + "☆" * (5 - llenas)

def calcular_totales():
    subtotal = total_carrito()
    envio = 0 if subtotal >= ENVIO_GRATIS_DESDE else ENVIO_BASE
    descuento = 0
    if st.session_state.coupon:
        info = CUPONES.get(st.session_state.coupon)
        if info:
            if info["tipo"] == "porcentaje" and subtotal >= info["min"]:
                descuento = subtotal * (info["desc"] / 100)
            elif info["tipo"] == "envio_gratis":
                envio = 0
    iva = (subtotal - descuento) * IVA
    return subtotal, envio, descuento, iva, (subtotal - descuento + envio + iva)

def ir_a(page, pid=None):
    st.session_state.page = page
    if pid is not None:
        st.session_state.selected_product = pid
        st.session_state.selected_image_index = 0
    st.rerun()

def agregar_carrito(p, cant=1):
    precio, _ = precio_desc(p)
    pid = p["id"]
    if pid in st.session_state.carrito:
        st.session_state.carrito[pid]["cantidad"] += cant
    else:
        st.session_state.carrito[pid] = {
            "title": p["title"], "price": precio,
            "image": p["thumbnail"], "cantidad": cant,
        }

def click_categoria(label):
    st.session_state.grupo_sel = label
    st.session_state.cat_especifica = "Todas"
    st.session_state.page = "home"
    st.rerun()


st.markdown(h("""
<div class="utility-bar">
    <a href="#">buscador de tiendas</a>
    <a href="#">ayuda</a>
    <a href="#">pedidos y devoluciones</a>
    <a href="#">tarjetas regalo</a>
    <a href="#">únete al club</a>
</div>
"""), unsafe_allow_html=True)


col_logo, col_search, col_icons = st.columns([3, 5, 3], gap="small")

with col_logo:
    st.markdown(h("""
    <div style="padding-top:10px;">
        <div class="brand-logo">
            <div class="brand-mark">N</div>
            Nova<span class="accent">Shop</span>
        </div>
    </div>
    """), unsafe_allow_html=True)

with col_search:
    busqueda = st.text_input(
        "Buscar", placeholder="Buscar productos, marcas...",
        label_visibility="collapsed", key="search_input"
    )

with col_icons:
    st.markdown('<div class="icon-buttons">', unsafe_allow_html=True)
    ic1, ic2, ic3 = st.columns(3)
    with ic1:
        if st.button("👤", key="ic_user", use_container_width=True):
            st.toast("Perfil de usuario", icon="👤")
    with ic2:
        if st.button("🤍", key=f"ic_wish_{len(st.session_state.wishlist)}", use_container_width=True):
            ir_a("wishlist")
    with ic3:
        if st.button("🛒", key=f"ic_cart_{cant_carrito()}", use_container_width=True):
            ir_a("cart")
    st.markdown('</div>', unsafe_allow_html=True)


st.markdown('<div class="nav-buttons">', unsafe_allow_html=True)
nav_items = [
    ("👩 Mujer", "nav_mujer"),
    ("👨 Hombre", "nav_hombre"),
    ("💄 Belleza", "nav_belleza"),
    ("📱 Tecnología", "nav_tec"),
    ("🏠 Hogar", "nav_hogar"),
    ("🔥 Ofertas", "nav_ofertas"),
]
nav_cols = st.columns(len(nav_items), gap="small")
for i, (label, slug) in enumerate(nav_items):
    with nav_cols[i]:
        if st.button(label, key=slug, use_container_width=True):
            click_categoria(label)
st.markdown('</div>', unsafe_allow_html=True)


st.markdown(h("""
<div class="promo-banner">
    <b>NOVASHOP FESTIVAL YA LLEGÓ.</b> INICIA SESIÓN Y APROVECHA OFERTAS, PREMIOS Y SORPRESAS.
    <span class="arrow">→</span>
</div>
"""), unsafe_allow_html=True)


def render_sidebar():
    grupos_opts = list(GRUPOS_FILTRO.keys())

    if st.session_state.grupo_sel not in grupos_opts:
        st.session_state.grupo_sel = "Todas"

    with st.sidebar:
        st.markdown("### 🔍 Filtros")
        st.markdown("---")

        st.markdown("**Categoría rápida**")
        grupo_sel = st.selectbox(
            "Grupo",
            grupos_opts,
            key="grupo_sel",
            label_visibility="collapsed"
        )

        st.markdown("---")

        grupo_cats = GRUPOS_FILTRO.get(grupo_sel)
        if grupo_cats and grupo_cats != "OFERTAS":
            cats_disponibles = sorted(grupo_cats, key=lambda x: cat_es(x))
        else:
            cats_disponibles = sorted(set(p["category"] for p in PRODUCTOS), key=lambda x: cat_es(x))

        if st.session_state.cat_especifica not in ["Todas"] + cats_disponibles:
            st.session_state.cat_especifica = "Todas"

        st.markdown("**Categoría específica**")
        cat_sel = st.selectbox(
            "Categoría",
            ["Todas"] + cats_disponibles,
            format_func=lambda x: "Todas" if x == "Todas" else cat_es(x),
            key="cat_especifica",
            label_visibility="collapsed"
        )

        st.markdown("---")

        st.markdown("**Marca**")
        if grupo_cats and grupo_cats != "OFERTAS":
            marcas = sorted(set(p.get("brand", "") for p in PRODUCTOS if p.get("brand") and p["category"] in grupo_cats))
        else:
            marcas = sorted(set(p.get("brand", "") for p in PRODUCTOS if p.get("brand")))

        if st.session_state.marca_sel not in ["Todas"] + marcas:
            st.session_state.marca_sel = "Todas"

        marca_sel = st.selectbox(
            "Marca", ["Todas"] + marcas,
            key="marca_sel",
            label_visibility="collapsed"
        )

        st.markdown("---")

        st.markdown("**Rango de precio**")
        precios = [p["price"] for p in PRODUCTOS]
        max_precio = float(max(precios))
        if "rango_precio" not in st.session_state or st.session_state.rango_precio[1] > max_precio:
            st.session_state.rango_precio = (0.0, max_precio)
        rango = st.slider(
            "Precio",
            0.0, max_precio,
            key="rango_precio",
            label_visibility="collapsed"
        )

        st.markdown("---")

        st.markdown("**Calificación mínima**")
        rating_min = st.select_slider(
            "Rating",
            options=[0, 1, 2, 3, 4, 4.5, 5],
            key="rating_min",
            label_visibility="collapsed"
        )

        st.markdown("---")

        st.markdown("**Otros filtros**")
        solo_ofertas = st.checkbox("Solo productos en oferta 🔥", key="solo_ofertas_chk")
        solo_stock = st.checkbox("Solo con stock disponible", key="solo_stock_chk")

        st.markdown("---")

        st.markdown("### 🎟️ Cupones disponibles")
        st.markdown(h("""
        <div style="background:linear-gradient(135deg,#EEF2FF,#F5F3FF); border:1px dashed #6366F1; border-radius:6px; padding:10px 12px; margin-bottom:8px;">
            <div style="font-family:monospace; font-weight:800; color:#4338CA; font-size:14px; letter-spacing:1px;">NOVA10</div>
            <div style="font-size:11px; color:#4B5563; font-weight:600;">10% de descuento</div>
        </div>
        """), unsafe_allow_html=True)
        st.markdown(h("""
        <div style="background:linear-gradient(135deg,#EEF2FF,#F5F3FF); border:1px dashed #6366F1; border-radius:6px; padding:10px 12px; margin-bottom:8px;">
            <div style="font-family:monospace; font-weight:800; color:#4338CA; font-size:14px; letter-spacing:1px;">NOVA20</div>
            <div style="font-size:11px; color:#4B5563; font-weight:600;">20% · Compra mínima $100</div>
        </div>
        """), unsafe_allow_html=True)
        st.markdown(h("""
        <div style="background:linear-gradient(135deg,#ECFDF5,#F0FDF4); border:1px dashed #10B981; border-radius:6px; padding:10px 12px; margin-bottom:8px;">
            <div style="font-family:monospace; font-weight:800; color:#047857; font-size:14px; letter-spacing:1px;">BIENVENIDO</div>
            <div style="font-size:11px; color:#4B5563; font-weight:600;">5% de descuento</div>
        </div>
        """), unsafe_allow_html=True)
        st.markdown(h("""
        <div style="background:linear-gradient(135deg,#FEF3C7,#FFFBEB); border:1px dashed #F59E0B; border-radius:6px; padding:10px 12px; margin-bottom:8px;">
            <div style="font-family:monospace; font-weight:800; color:#B45309; font-size:14px; letter-spacing:1px;">ENVIOGRATIS</div>
            <div style="font-size:11px; color:#4B5563; font-weight:600;">Envío sin costo</div>
        </div>
        """), unsafe_allow_html=True)

    filtrados = PRODUCTOS

    if grupo_sel == "🔥 Ofertas":
        filtrados = [p for p in filtrados if p.get("discountPercentage", 0) > 10]
    elif grupo_cats:
        filtrados = [p for p in filtrados if p["category"] in grupo_cats]

    if busqueda:
        filtrados = [p for p in filtrados if busqueda.lower() in p["title"].lower() or busqueda.lower() in p.get("brand", "").lower()]
    if cat_sel != "Todas":
        filtrados = [p for p in filtrados if p["category"] == cat_sel]
    if marca_sel != "Todas":
        filtrados = [p for p in filtrados if p.get("brand") == marca_sel]
    filtrados = [p for p in filtrados if rango[0] <= p["price"] <= rango[1]]
    filtrados = [p for p in filtrados if p.get("rating", 0) >= rating_min]
    if solo_ofertas:
        filtrados = [p for p in filtrados if p.get("discountPercentage", 0) > 10]
    if solo_stock:
        filtrados = [p for p in filtrados if p.get("stock", 0) > 0]

    return filtrados, cat_sel, marca_sel, grupo_sel


def render_card(p, key_prefix="c"):
    precio, precio_orig = precio_desc(p)
    desc = p.get("discountPercentage", 0)
    rating = p.get("rating", 0)
    stock = p.get("stock", 0)

    tag_new = '<div class="ml-tag-new">NUEVO</div>' if p["id"] % 7 == 0 else ''
    tag_off = f'<div class="ml-tag-off">-{int(desc)}%</div>' if desc > 5 else ''
    envio_html = '<div class="ml-shipping">🚚 Envío gratis <span class="ml-full-badge">FULL</span></div>' if p["price"] > 50 else ''
    desc_html = f'<span class="ml-discount">{int(desc)}% OFF</span>' if desc > 5 else ''
    old_html = f'<div class="ml-old-price">${precio_orig:.0f}</div>' if desc > 5 else ''
    estrellas = estrellas_html(rating)

    st.markdown(h(f"""
    <div class="ml-card">
        {tag_new}{tag_off}
        <div class="ml-img-box"><img src="{p['thumbnail']}" /></div>
        <div class="ml-price-row"><span class="ml-price">${precio:.0f}</span>{desc_html}</div>
        {old_html}
        <div class="ml-title">{p['title']}</div>
        <div class="ml-rating-row">
            <span class="ml-stars-gold">{estrellas}</span>
            <span class="ml-rating-num">{rating:.1f}</span>
        </div>
        {envio_html}
    </div>
    """), unsafe_allow_html=True)

    b1, b2, b3 = st.columns([2, 1, 1])
    with b1:
        if st.button("🛒 Agregar", key=f"{key_prefix}_add_{p['id']}", disabled=(stock == 0), use_container_width=True):
            agregar_carrito(p)
            st.toast(f"✅ Agregado: {p['title'][:25]}...", icon="🛒")
            st.rerun()
    with b2:
        corazon = "❤️" if p["id"] in st.session_state.wishlist else "🤍"
        if st.button(corazon, key=f"{key_prefix}_w_{p['id']}", use_container_width=True):
            if p["id"] in st.session_state.wishlist:
                st.session_state.wishlist.remove(p["id"])
            else:
                st.session_state.wishlist.add(p["id"])
            st.rerun()
    with b3:
        if st.button("👁️", key=f"{key_prefix}_v_{p['id']}", use_container_width=True):
            if p["id"] in st.session_state.recently_viewed:
                st.session_state.recently_viewed.remove(p["id"])
            st.session_state.recently_viewed.insert(0, p["id"])
            st.session_state.recently_viewed = st.session_state.recently_viewed[:8]
            ir_a("product", p["id"])


def render_footer():
    st.markdown(h("""
    <div class="footer-container">
        <div class="footer-grid">
            <div class="footer-col">
                <h4 class="footer-title">PRODUCTOS</h4>
                <a href="#">Tenis</a>
                <a href="#">Ropa</a>
                <a href="#">Accesorios</a>
                <a href="#">Novedades</a>
                <a href="#">Outlet</a>
                <a href="#">Ofertas</a>
                <a href="#">Black Friday</a>
                <a href="#">Cyber Monday</a>
                <a href="#">Hot Sale</a>
                <a href="#">Lo más vendido</a>
            </div>
            <div class="footer-col">
                <h4 class="footer-title">COLECCIONES</h4>
                <a href="#">NovaClub</a>
                <a href="#">Edición Limitada</a>
                <a href="#">Originals</a>
                <a href="#">Premium</a>
                <a href="#">Deportes</a>
                <a href="#">Casual</a>
                <a href="#">Formal</a>
                <a href="#">Verano 2025</a>
            </div>
            <div class="footer-col">
                <h4 class="footer-title">SOPORTE</h4>
                <a href="#">Cambios y devoluciones</a>
                <a href="#">Cómo comprar</a>
                <a href="#">Mapa del sitio</a>
                <a href="#">Buscador de tiendas</a>
                <a href="#">Estado de mi pedido</a>
                <a href="#">Métodos de pago</a>
                <a href="#">Facturación</a>
                <a href="#">Preguntas frecuentes</a>
            </div>
            <div class="footer-col">
                <h4 class="footer-title">NUESTRO MUNDO</h4>
                <a href="#">Sobre NovaShop</a>
                <a href="#">Sustentabilidad</a>
                <a href="#">Personas</a>
                <a href="#">Planeta</a>
                <a href="#">Comunidad</a>
                <a href="#">Trabaja con nosotros</a>
                <a href="#">Prensa</a>
            </div>
            <div class="footer-col footer-social">
                <h4 class="footer-title">SÍGUENOS</h4>
                <div class="social-icons">
                    <span>📷</span>
                    <span>🎵</span>
                    <span>▶️</span>
                    <span>📘</span>
                    <span>🐦</span>
                </div>
                <div class="footer-club">
                    <div class="club-badge">🏆</div>
                    <div class="club-text">
                        <b>NOVACLUB</b>
                        <span>Únete y obtén 15% OFF</span>
                    </div>
                </div>
            </div>
        </div>
        <div class="footer-bottom">
            <div class="footer-legal">
                <a href="#">Configuración de cookies</a>
                <span>|</span>
                <a href="#">Términos y Condiciones</a>
                <span>|</span>
                <a href="#">Uso del sitio</a>
                <span>|</span>
                <a href="#">Términos de promociones</a>
                <span>|</span>
                <a href="#">Privacidad</a>
                <span>|</span>
                <a href="#">Seleccionar país</a>
                <span>|</span>
                <a href="#">Aviso de privacidad</a>
            </div>
            <div class="footer-copy">© 2025 NovaShop S.A. de C.V. · Todos los derechos reservados</div>
        </div>
    </div>
    """), unsafe_allow_html=True)


def page_home():
    filtrados, cat_sel, marca_sel, grupo_sel = render_sidebar()

    if grupo_sel == "Todas" and cat_sel == "Todas" and not busqueda:
        img1 = next((p["thumbnail"] for p in PRODUCTOS if p["category"] == "womens-dresses"), PRODUCTOS[0]["thumbnail"])
        img2 = next((p["thumbnail"] for p in PRODUCTOS if p["category"] == "mens-shirts"), PRODUCTOS[1]["thumbnail"])
        img3 = next((p["thumbnail"] for p in PRODUCTOS if p["category"] == "womens-shoes"), PRODUCTOS[2]["thumbnail"])

        st.markdown(h(f"""
        <div class="hero-grid">
            <div class="hero-black">
                <h2 class="hero-black-title">TUS<br/>DESCUENTOS<br/>SE SUMAN 💚</h2>
                <p class="hero-black-sub">Aprovecha productos seleccionados con descuento y suma de <b>15% a 30% adicional</b> con tus cupones NovaClub.</p>
                <div class="hero-black-btn">VER TODO</div>
            </div>
            <div class="hero-cats">
                <div class="hero-cat">
                    <div class="hero-cat-label">Mujer</div>
                    <img src="{img1}" />
                </div>
                <div class="hero-cat">
                    <div class="hero-cat-label">Hombre</div>
                    <img src="{img2}" />
                </div>
                <div class="hero-cat">
                    <div class="hero-cat-label">Niños</div>
                    <img src="{img3}" />
                </div>
            </div>
        </div>
        """), unsafe_allow_html=True)

    grupo_txt = grupo_sel if grupo_sel != "Todas" else "Todos los productos"
    st.markdown(f'<div class="ml-section-title">{grupo_txt} · {len(filtrados)} productos</div>', unsafe_allow_html=True)

    c1, c2 = st.columns([3, 1])
    with c1:
        cat_txt = "Todas" if cat_sel == "Todas" else cat_es(cat_sel)
        st.caption(f"📍 **{grupo_txt}** · Categoría: **{cat_txt}** · Marca: **{marca_sel}**")
    with c2:
        orden = st.selectbox("Orden", ["Relevancia", "Precio ↑", "Precio ↓", "Mejor calificados", "Mayor descuento"], label_visibility="collapsed")

    if orden == "Precio ↑": filtrados = sorted(filtrados, key=lambda x: x["price"])
    elif orden == "Precio ↓": filtrados = sorted(filtrados, key=lambda x: x["price"], reverse=True)
    elif orden == "Mejor calificados": filtrados = sorted(filtrados, key=lambda x: x.get("rating", 0), reverse=True)
    elif orden == "Mayor descuento": filtrados = sorted(filtrados, key=lambda x: x.get("discountPercentage", 0), reverse=True)

    if not filtrados:
        st.warning("😕 No se encontraron productos con esos filtros.")
    else:
        cols = st.columns(4, gap="small")
        for i, p in enumerate(filtrados[:36]):
            with cols[i % 4]:
                render_card(p, "home")

        if st.session_state.recently_viewed:
            st.markdown('<div class="ml-section-title">👀 Vistos recientemente</div>', unsafe_allow_html=True)
            cols_rv = st.columns(4, gap="small")
            for i, pid in enumerate(st.session_state.recently_viewed[:4]):
                prod = next((p for p in PRODUCTOS if p["id"] == pid), None)
                if prod:
                    with cols_rv[i]:
                        render_card(prod, "rv")

    render_footer()


def page_product():
    p = get_product_by_id(st.session_state.selected_product)
    if not p:
        st.error("Producto no encontrado.")
        if st.button("← Volver"):
            ir_a("home")
        return

    if st.button("← Volver al catálogo", key="back_home"):
        ir_a("home")

    precio, precio_orig = precio_desc(p)
    desc = p.get("discountPercentage", 0)
    ahorro = precio_orig - precio
    stock = p.get("stock", 0)
    imgs = p.get("images", [p.get("thumbnail")])
    idx = st.session_state.selected_image_index
    rating = p.get("rating", 0)
    estrellas = estrellas_html(rating)
    reviews = p.get("reviews", [])
    cat_traducida = cat_es(p["category"])

    col_gallery, col_info = st.columns([1, 1.4], gap="medium")

    with col_gallery:
        st.markdown(h(f'<div class="ml-detail-card" style="padding:20px; text-align:center;"><img src="{imgs[idx]}" style="max-width:100%; max-height:420px; object-fit:contain;" /></div>'), unsafe_allow_html=True)
        if len(imgs) > 1:
            tcols = st.columns(min(len(imgs), 4))
            for i, img in enumerate(imgs[:4]):
                with tcols[i]:
                    border = "2px solid #111827" if i == idx else "1px solid #E5E7EB"
                    st.markdown(h(f'<div style="border:{border}; border-radius:4px; padding:6px; height:60px; display:flex; align-items:center; justify-content:center; margin-bottom:6px;"><img src="{img}" style="max-height:100%; max-width:100%; object-fit:contain;" /></div>'), unsafe_allow_html=True)
                    if st.button(f"Ver {i+1}", key=f"thumb_{p['id']}_{i}", use_container_width=True):
                        st.session_state.selected_image_index = i
                        st.rerun()

    with col_info:
        envio_html = '<div class="ml-detail-shipping">🚚 Envío gratis <span class="ml-full-badge">FULL</span> · Llega en 24-48h</div>'
        desc_html = f'<span class="ml-detail-discount">{int(desc)}% OFF</span>' if desc > 5 else ''
        old_html = f'<div class="ml-detail-old">Antes: ${precio_orig:.2f} · Ahorras ${ahorro:.2f}</div>' if desc > 5 else ''

        if stock == 0:
            stock_html = '<div class="ml-stock-out">❌ Producto agotado</div>'
        elif stock < 10:
            stock_html = f'<div class="ml-stock-low">⚡ ¡Solo quedan {stock} unidades!</div>'
        else:
            stock_html = f'<div class="ml-stock-good">✅ En stock · {stock} disponibles</div>'

        st.markdown(h(f"""
        <div class="ml-detail-card">
            <div class="ml-detail-meta">{p.get('brand','NovaShop')} · {cat_traducida} · Vendido por NovaShop</div>
            <div class="ml-detail-title">{p['title']}</div>
            <div style="margin: 8px 0; font-size: 14px; color:#6B7280;">
                <span class="ml-stars-big">{estrellas}</span>
                <b style="color:#111827;"> {rating:.1f}</b> · {len(reviews)} opiniones
            </div>
            <div class="ml-detail-price">${precio:.2f} {desc_html}</div>
            {old_html}
            {envio_html}
            {stock_html}
            <p style="color:#4B5563; line-height:1.6; margin-top:16px; font-size:14px;">{p.get('description','')}</p>
            <div style="border-top:1px solid #F3F4F6; padding-top:16px; margin-top:16px;">
                <div class="ml-feature-item">🔄 <b>Devolución gratis</b> · 30 días</div>
                <div class="ml-feature-item">🔒 <b>Compra protegida</b> · Pago 100% seguro</div>
                <div class="ml-feature-item">🏆 <b>Garantía</b> · {p.get('warrantyInformation','1 año')}</div>
            </div>
        </div>
        """), unsafe_allow_html=True)

        st.write("")
        c1, c2 = st.columns([1, 3])
        with c1:
            cant = st.number_input("Cantidad", min_value=1, max_value=max(1, stock), value=1, key="det_cant")
        with c2:
            st.write("")
            if st.button("🛒 Agregar al carrito", key="det_add", disabled=(stock == 0), use_container_width=True, type="primary"):
                agregar_carrito(p, cant)
                st.toast(f"✅ {cant} agregado(s)", icon="🛒")
                st.rerun()

        c1, c2 = st.columns(2)
        with c1:
            if st.button("⚡ Comprar ahora", key="det_buy", disabled=(stock == 0), use_container_width=True):
                st.session_state.carrito[p["id"]] = {
                    "title": p["title"], "price": precio,
                    "image": p["thumbnail"], "cantidad": cant,
                }
                ir_a("checkout")
        with c2:
            corazon = "❤️ En favoritos" if p["id"] in st.session_state.wishlist else "🤍 Favoritos"
            if st.button(corazon, key="det_w", use_container_width=True):
                if p["id"] in st.session_state.wishlist:
                    st.session_state.wishlist.remove(p["id"])
                else:
                    st.session_state.wishlist.add(p["id"])
                st.rerun()

    st.markdown('<div class="ml-section-title">📋 Especificaciones</div>', unsafe_allow_html=True)
    peso = p.get("weight", 0)
    dims = p.get("dimensions", {})
    specs_data = [
        ("Marca", p.get("brand", "NovaShop")),
        ("Categoría", cat_traducida),
        ("Peso", f"{peso} kg"),
        ("Ancho", f"{dims.get('width', 'N/A')} cm"),
        ("Alto", f"{dims.get('height', 'N/A')} cm"),
        ("Garantía", p.get("warrantyInformation", "1 año")),
        ("Envío", p.get("shippingInformation", "24-48 horas")),
        ("Política de devolución", p.get("returnPolicy", "30 días")),
        ("Estado", p.get("availabilityStatus", "Disponible")),
        ("SKU", p.get("sku", "N/A")),
    ]
    sc1, sc2 = st.columns(2)
    for i, (label, value) in enumerate(specs_data):
        target = sc1 if i % 2 == 0 else sc2
        with target:
            st.markdown(h(f'<div style="background:white; padding:10px 14px; border-radius:4px; margin-bottom:8px; display:flex; justify-content:space-between; font-size:13px; box-shadow:0 0 0 1px #F3F4F6;"><span style="color:#6B7280; font-weight:600;">{label}</span><span style="color:#111827; font-weight:700;">{value}</span></div>'), unsafe_allow_html=True)

    st.markdown('<div class="ml-section-title">💬 Opiniones de clientes</div>', unsafe_allow_html=True)
    if reviews:
        for r in reviews[:4]:
            inicial = r.get("reviewerName", "A")[0].upper()
            r_est = estrellas_html(r.get("rating", 5))
            st.markdown(h(f"""
            <div class="ml-detail-card" style="margin-bottom:12px; padding:16px 20px;">
                <div style="display:flex; align-items:center; gap:12px; margin-bottom:8px;">
                    <div style="width:40px; height:40px; border-radius:50%; background:#111827; color:white; display:flex; align-items:center; justify-content:center; font-weight:700;">{inicial}</div>
                    <div>
                        <div style="font-weight:700; color:#111827;">{r.get('reviewerName','Anónimo')}</div>
                        <div style="font-size:11px; color:#9CA3AF;">{r.get('date','')[:10]}</div>
                    </div>
                    <div style="margin-left:auto;" class="ml-stars-big">{r_est}</div>
                </div>
                <div style="color:#4B5563; font-size:14px; line-height:1.5;">"{r.get('comment','')}"</div>
            </div>
            """), unsafe_allow_html=True)
    else:
        st.info("Este producto aún no tiene opiniones.")

    st.markdown('<div class="ml-section-title">🎯 También te puede interesar</div>', unsafe_allow_html=True)
    relacionados = [x for x in PRODUCTOS if x["category"] == p["category"] and x["id"] != p["id"]][:4]
    if relacionados:
        rcols = st.columns(4, gap="small")
        for i, rp in enumerate(relacionados):
            with rcols[i]:
                render_card(rp, "rel")

    render_footer()


def page_cart():
    st.markdown('<div class="ml-section-title">🛒 Tu carrito</div>', unsafe_allow_html=True)
    if st.button("← Seguir comprando", key="cart_back"):
        ir_a("home")

    if not st.session_state.carrito:
        st.info("🛍️ Tu carrito está vacío.")
        return

    col_items, col_resumen = st.columns([1.8, 1], gap="medium")

    with col_items:
        for pid, item in list(st.session_state.carrito.items()):
            c_img, c_info, c_qty, c_price, c_del = st.columns([1, 3, 2, 1.3, 0.6])
            with c_img:
                st.markdown(h(f'<div class="ml-cart-img"><img src="{item["image"]}" /></div>'), unsafe_allow_html=True)
            with c_info:
                st.markdown(f"**{item['title'][:70]}**")
                st.caption(f"Unitario: ${item['price']:.2f}")
            with c_qty:
                q1, q2, q3 = st.columns([1, 1, 1])
                with q1:
                    if st.button("−", key=f"cm_{pid}"):
                        if st.session_state.carrito[pid]["cantidad"] > 1:
                            st.session_state.carrito[pid]["cantidad"] -= 1
                        st.rerun()
                with q2:
                    st.markdown(f"<div style='text-align:center; padding-top:8px; font-weight:700;'>{item['cantidad']}</div>", unsafe_allow_html=True)
                with q3:
                    if st.button("+", key=f"cp_{pid}"):
                        st.session_state.carrito[pid]["cantidad"] += 1
                        st.rerun()
            with c_price:
                st.markdown(f"<div style='padding-top:8px; font-weight:700; color:#111827;'>${item['price']*item['cantidad']:.2f}</div>", unsafe_allow_html=True)
            with c_del:
                if st.button("🗑️", key=f"cd_{pid}"):
                    del st.session_state.carrito[pid]
                    st.rerun()
            st.markdown("---")

    with col_resumen:
        subtotal, envio, descuento, iva, total = calcular_totales()
        envio_txt = "GRATIS" if envio == 0 else f"${envio:.2f}"
        descuento_html = f'<div class="ml-summary-row" style="color:#059669;"><span>Descuento ({st.session_state.coupon})</span><span>-${descuento:.2f}</span></div>' if descuento > 0 else ''
        envio_msg = '<div class="ml-free-shipping">🎉 ¡Tienes envío GRATIS!</div>' if envio == 0 else f'<div class="ml-free-shipping" style="background:#FFF7ED; color:#C2410C;">Te faltan ${ENVIO_GRATIS_DESDE - subtotal:.2f} para envío gratis</div>'

        st.markdown(h(f"""
        <div class="ml-summary">
            <h3 style="margin:0 0 16px 0; font-size:16px; color:#111827;">Resumen de compra</h3>
            <div class="ml-summary-row"><span>Productos ({cant_carrito()})</span><span>${subtotal:.2f}</span></div>
            <div class="ml-summary-row"><span>Envío</span><span style="color:#059669; font-weight:700;">{envio_txt}</span></div>
            {descuento_html}
            <div class="ml-summary-row"><span>IVA (16%)</span><span>${iva:.2f}</span></div>
            <div class="ml-summary-total"><span>Total</span><span>${total:.2f}</span></div>
            {envio_msg}
        </div>
        """), unsafe_allow_html=True)

        st.write("")
        cupon_input = st.text_input("🎟️ Cupón", placeholder="Ej: NOVA10", label_visibility="collapsed")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Aplicar", key="apply_cp", use_container_width=True):
                if cupon_input.upper() in CUPONES:
                    st.session_state.coupon = cupon_input.upper()
                    st.toast("✅ Cupón aplicado", icon="🎟️")
                    st.rerun()
                else:
                    st.error("❌ Cupón inválido")
        with c2:
            if st.session_state.coupon and st.button("Quitar", key="rm_cp", use_container_width=True):
                st.session_state.coupon = None
                st.rerun()

        st.write("")
        if st.button("💳 Iniciar compra", key="go_checkout", use_container_width=True, type="primary"):
            ir_a("checkout")


def page_wishlist():
    st.markdown('<div class="ml-section-title">❤️ Mis favoritos</div>', unsafe_allow_html=True)
    if st.button("← Volver al inicio", key="wl_back"):
        ir_a("home")
    if not st.session_state.wishlist:
        st.info("💔 Aún no tienes productos en favoritos.")
        return
    favs = [p for p in PRODUCTOS if p["id"] in st.session_state.wishlist]
    cols = st.columns(4, gap="small")
    for i, p in enumerate(favs):
        with cols[i % 4]:
            render_card(p, "wl")


def page_checkout():
    st.markdown('<div class="ml-section-title">💳 Finalizar compra</div>', unsafe_allow_html=True)

    st.markdown(h("""
    <div class="ml-steps">
        <div class="ml-step done"><div class="ml-step-num">✓</div> Carrito</div>
        <div class="ml-step active"><div class="ml-step-num">2</div> Datos de envío</div>
        <div class="ml-step"><div class="ml-step-num">3</div> Confirmación</div>
    </div>
    """), unsafe_allow_html=True)

    if not st.session_state.carrito:
        st.warning("Tu carrito está vacío.")
        if st.button("← Volver"):
            ir_a("home")
        return

    if st.button("← Volver al carrito", key="co_back"):
        ir_a("cart")

    col_form, col_resumen = st.columns([1.5, 1], gap="medium")

    with col_form:
        with st.form("checkout_form"):
            st.markdown('<h3 style="color:#111827; margin-top:0;">📦 Datos de envío</h3>', unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                nombre = st.text_input("Nombre completo *")
            with c2:
                email = st.text_input("Correo electrónico *")
            c1, c2 = st.columns([2, 1])
            with c1:
                direccion = st.text_input("Dirección *")
            with c2:
                cp = st.text_input("Código postal *")
            c1, c2, c3 = st.columns(3)
            with c1:
                ciudad = st.text_input("Ciudad *")
            with c2:
                estado = st.text_input("Estado *")
            with c3:
                telefono = st.text_input("Teléfono *")

            st.markdown('<h3 style="color:#111827; margin-top:24px;">💳 Método de pago</h3>', unsafe_allow_html=True)
            metodo = st.radio("Selecciona:", ["Tarjeta de crédito/débito", "PayPal", "Pago contra entrega"], horizontal=True)

            if metodo == "Tarjeta de crédito/débito":
                st.text_input("Número de tarjeta", placeholder="1234 5678 9012 3456")
                c1, c2, c3 = st.columns([2, 1, 1])
                with c1:
                    st.text_input("Nombre en la tarjeta")
                with c2:
                    st.text_input("Vencimiento", placeholder="MM/AA")
                with c3:
                    st.text_input("CVV", type="password")

            enviado = st.form_submit_button("✅ Confirmar pedido", use_container_width=True)

            if enviado:
                if not all([nombre, email, direccion, cp, ciudad, estado, telefono]):
                    st.error("⚠️ Completa todos los campos obligatorios.")
                else:
                    subtotal, envio, descuento, iva, total = calcular_totales()
                    num_orden = f"NOVA-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000,9999)}"
                    fecha = (datetime.now() + timedelta(days=3)).strftime("%d/%m/%Y")
                    st.session_state.order = {
                        "numero": num_orden, "fecha_entrega": fecha,
                        "items": list(st.session_state.carrito.values()),
                        "subtotal": subtotal, "descuento": descuento,
                        "envio": envio, "iva": iva, "total": total,
                        "cliente": {"nombre": nombre, "email": email,
                                    "direccion": f"{direccion}, {ciudad}, {estado}, CP {cp}",
                                    "telefono": telefono},
                        "metodo": metodo,
                    }
                    st.session_state.carrito = {}
                    st.session_state.coupon = None
                    ir_a("confirmation")

    with col_resumen:
        subtotal, envio, descuento, iva, total = calcular_totales()
        envio_txt = "GRATIS" if envio == 0 else f"${envio:.2f}"

        items_html = ""
        for item in st.session_state.carrito.values():
            items_html += h(f'<div style="display:flex; gap:10px; padding:10px 0; border-bottom:1px solid #F3F4F6;"><img src="{item["image"]}" style="width:50px; height:50px; object-fit:contain; background:#F9FAFB; border-radius:4px; padding:4px;"/><div style="flex:1; font-size:12px;"><div style="font-weight:600; color:#111827;">{item["title"][:40]}...</div><div style="color:#6B7280;">{item["cantidad"]} × ${item["price"]:.2f}</div></div><div style="font-weight:700; color:#111827;">${item["price"]*item["cantidad"]:.2f}</div></div>')

        descuento_html = f'<div class="ml-summary-row" style="color:#059669;"><span>Descuento</span><span>-${descuento:.2f}</span></div>' if descuento > 0 else ''

        st.markdown(h(f"""
        <div class="ml-summary">
            <h3 style="margin:0 0 12px 0; font-size:16px; color:#111827;">Tu pedido ({cant_carrito()})</h3>
            {items_html}
            <div style="margin-top:16px;">
                <div class="ml-summary-row"><span>Subtotal</span><span>${subtotal:.2f}</span></div>
                <div class="ml-summary-row"><span>Envío</span><span style="color:#059669; font-weight:700;">{envio_txt}</span></div>
                {descuento_html}
                <div class="ml-summary-row"><span>IVA (16%)</span><span>${iva:.2f}</span></div>
                <div class="ml-summary-total"><span>Total</span><span>${total:.2f}</span></div>
            </div>
            <div style="background:#ECFDF5; padding:12px; border-radius:4px; margin-top:16px; font-size:12px; color:#059669; text-align:center;">
                🔒 Compra protegida con cifrado SSL
            </div>
        </div>
        """), unsafe_allow_html=True)


def page_confirmation():
    order = st.session_state.order
    if not order:
        ir_a("home")
        return

    st.markdown(h(f"""
    <div class="ml-success">
        <div class="ml-success-icon">✓</div>
        <div class="ml-success-title">¡Gracias por tu compra!</div>
        <div class="ml-success-sub">Enviamos la confirmación a <b>{order['cliente']['email']}</b></div>
        <div class="ml-order-num">Orden: {order['numero']}</div>
        <div style="color:#6B7280; font-size:14px;">📦 Entrega estimada: <b>{order['fecha_entrega']}</b></div>
    </div>
    """), unsafe_allow_html=True)

    c1, c2 = st.columns(2, gap="medium")

    with c1:
        st.markdown(h(f"""
        <div class="ml-detail-card">
            <h3 style="margin-top:0; color:#111827;">📋 Detalles del envío</h3>
            <div style="font-size:14px; color:#6B7280; line-height:2;">
                <b style="color:#111827;">Destinatario:</b> {order['cliente']['nombre']}<br/>
                <b style="color:#111827;">Dirección:</b> {order['cliente']['direccion']}<br/>
                <b style="color:#111827;">Teléfono:</b> {order['cliente']['telefono']}<br/>
                <b style="color:#111827;">Método de pago:</b> {order['metodo']}
            </div>
        </div>
        """), unsafe_allow_html=True)

    with c2:
        items_html = ""
        for item in order["items"]:
            items_html += f'<div style="display:flex; justify-content:space-between; font-size:13px; margin-bottom:8px;"><span style="color:#111827;">{item["cantidad"]}× {item["title"][:30]}...</span><b style="color:#111827;">${item["price"]*item["cantidad"]:.2f}</b></div>'

        descuento_html = f'<div class="ml-summary-row" style="color:#059669;"><span>Descuento</span><span>-${order["descuento"]:.2f}</span></div>' if order['descuento'] > 0 else ''

        st.markdown(h(f"""
        <div class="ml-detail-card">
            <h3 style="margin-top:0; color:#111827;">🧾 Recibo</h3>
            {items_html}
            <div style="border-top:1px solid #F3F4F6; margin-top:14px; padding-top:14px;">
                <div class="ml-summary-row"><span>Subtotal</span><span>${order['subtotal']:.2f}</span></div>
                <div class="ml-summary-row"><span>Envío</span><span>{'GRATIS' if order['envio']==0 else f'${order["envio"]:.2f}'}</span></div>
                {descuento_html}
                <div class="ml-summary-row"><span>IVA</span><span>${order['iva']:.2f}</span></div>
                <div class="ml-summary-total"><span>Total</span><span>${order['total']:.2f}</span></div>
            </div>
        </div>
        """), unsafe_allow_html=True)

    st.write("")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🏠 Volver al inicio", key="conf_h", use_container_width=True, type="primary"):
            ir_a("home")
    with c2:
        if st.button("🛍️ Seguir comprando", key="conf_s", use_container_width=True):
            ir_a("home")


page = st.session_state.page
if page == "home": page_home()
elif page == "product": page_product()
elif page == "cart": page_cart()
elif page == "wishlist": page_wishlist()
elif page == "checkout": page_checkout()
elif page == "confirmation": page_confirmation()