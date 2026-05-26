import streamlit as st
import pandas as pd
from PIL import Image
import easyocr
import numpy as np
import re
import matplotlib.pyplot as plt
from rapidfuzz import fuzz
from datetime import datetime
from urllib.parse import quote

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="🔥 Warehouse AI Super App V8",
    page_icon="🔥",
    layout="wide"
)

# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

.main {
    background-color: #0E1117;
}

.block-container {
    padding-top: 1rem;
}

div[data-testid="metric-container"] {
    background-color: #1E1E1E;
    border: 1px solid #333;
    padding: 15px;
    border-radius: 12px;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# OCR LOADER
# =========================================================

@st.cache_resource
def load_reader():

    return easyocr.Reader(['en'])

reader = load_reader()

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("🔥 Warehouse AI Super App V8")

menu = st.sidebar.radio(

    "Pilih Menu",

    [

        "📦 Shipment Dashboard",
        "📊 Analytics",
        "🧠 AI Visual Search",
        "📷 Barcode Scanner"

    ]

)

st.sidebar.divider()

st.sidebar.success("System Online ✅")

# =========================================================
# FILE UPLOAD
# =========================================================

uploaded_file = st.sidebar.file_uploader(
    "Upload XLSX / CSV",
    type=["xlsx", "csv"]
)

df = None

if uploaded_file:

    try:

        if uploaded_file.name.endswith(".csv"):

            df = pd.read_csv(uploaded_file)

        else:

            df = pd.read_excel(uploaded_file)

        # CLEAN COLUMN
        df.columns = [

            str(col).strip()

            for col in df.columns

        ]

    except Exception as e:

        st.error(f"Error membaca file: {e}")

# =========================================================
# SMART SEARCH
# =========================================================

def smart_search_dataframe(dataframe, search):

    if not search:
        return dataframe

    shortcuts = {

        "cd": "celana dalam",
        "hp": "handphone",
        "rak": "rack",
        "tv": "television",
        "sepatu": "sneakers",
        "kaos": "baju"

    }

    search_text = search.lower()

    # SHORTCUT REPLACE
    for short, full in shortcuts.items():

        if short in search_text:

            search_text = search_text.replace(
                short,
                full
            )

    # SEARCH FUNCTION
    def smart_search(row):

        row_text = " ".join(
            map(str, row)
        ).lower()

        # EXACT SEARCH
        if search_text in row_text:
            return True

        # FUZZY SEARCH
        similarity = fuzz.partial_ratio(
            search_text,
            row_text
        )

        if similarity >= 70:
            return True

        return False

    filtered = dataframe[
        dataframe.apply(
            smart_search,
            axis=1
        )
    ]

    return filtered

# =========================================================
# AI CATEGORY
# =========================================================

def detect_category(text):

    text = str(text).lower()

    categories = {

        "👕 Fashion": [

            "celana",
            "baju",
            "hoodie",
            "kaos",
            "sepatu",
            "fashion",
            "tas"

        ],

        "🍳 Rumah Tangga": [

            "kompor",
            "rice cooker",
            "gelas",
            "piring",
            "miyako",
            "blender"

        ],

        "📱 Elektronik": [

            "hp",
            "laptop",
            "keyboard",
            "mouse",
            "monitor",
            "tv"

        ],

        "🪑 Furniture": [

            "rak",
            "lemari",
            "kursi",
            "meja",
            "cabinet"

        ],

        "🧸 Mainan": [

            "mainan",
            "lego",
            "boneka"

        ]

    }

    scores = {}

    for category, keywords in categories.items():

        score = 0

        for keyword in keywords:

            if keyword in text:

                score += 1

        scores[category] = score

    best_category = max(
        scores,
        key=scores.get
    )

    if scores[best_category] == 0:

        return "📦 Lainnya"

    return best_category

# =========================================================
# SHIPMENT DASHBOARD
# =========================================================

if menu == "📦 Shipment Dashboard":

    st.title("📦 Shipment Dashboard")

    if df is not None:

        # =============================================
        # CATEGORY
        # =============================================

        df["AI_Category"] = df.astype(str).apply(

            lambda row: detect_category(
                " ".join(map(str, row))
            ),

            axis=1
        )

        # =============================================
        # METRICS
        # =============================================

        col1, col2, col3, col4 = st.columns(4)

        with col1:

            st.metric(
                "Total Rows",
                len(df)
            )

        with col2:

            st.metric(
                "Columns",
                len(df.columns)
            )

        with col3:

            st.metric(
                "Duplicates",
                df.duplicated().sum()
            )

        with col4:

            try:

                unique_awb = (
                    df.iloc[:, 0]
                    .nunique()
                )

            except:

                unique_awb = 0

            st.metric(
                "Unique AWB",
                unique_awb
            )

        st.divider()

        # =============================================
        # SEARCH
        # =============================================

        search = st.text_input(

            "🔍 Smart Search",

            placeholder=(
                "Cari SKU, AWB, "
                "CD Shaka, HP Samsung..."
            )

        )

        filtered_df = smart_search_dataframe(
            df,
            search
        )

        # =============================================
        # CATEGORY FILTER
        # =============================================

        categories = sorted(
            filtered_df["AI_Category"]
            .unique()
        )

        selected_categories = st.multiselect(
            "🧠 Filter Category",
            categories
        )

        if selected_categories:

            filtered_df = filtered_df[
                filtered_df["AI_Category"]
                .isin(selected_categories)
            ]

        st.divider()

        # =============================================
        # STATUS FILTER
        # =============================================

        status_columns = [

            col for col in filtered_df.columns

            if (
                "status" in col.lower()
                or "desc" in col.lower()
            )

        ]

        if status_columns:

            selected_status_col = st.selectbox(
                "📦 Status Column",
                status_columns
            )

            status_options = sorted(

                filtered_df[
                    selected_status_col
                ]
                .astype(str)
                .dropna()
                .unique()

            )

            selected_status = st.multiselect(
                "Filter Status",
                status_options
            )

            if selected_status:

                filtered_df = filtered_df[

                    filtered_df[
                        selected_status_col
                    ]
                    .astype(str)
                    .isin(selected_status)

                ]

        st.divider()

        # =============================================
        # STATION FILTER
        # =============================================

        station_columns = [

            col for col in filtered_df.columns

            if (
                "station" in col.lower()
                or "origin" in col.lower()
                or "dest" in col.lower()
            )

        ]

        if station_columns:

            selected_station_col = st.selectbox(
                "📍 Station Column",
                station_columns
            )

            station_options = sorted(

                filtered_df[
                    selected_station_col
                ]
                .astype(str)
                .dropna()
                .unique()

            )

            selected_station = st.multiselect(
                "Filter Station",
                station_options
            )

            if selected_station:

                filtered_df = filtered_df[

                    filtered_df[
                        selected_station_col
                    ]
                    .astype(str)
                    .isin(selected_station)

                ]

        st.divider()

        # =============================================
        # SORT
        # =============================================

        col_sort1, col_sort2 = st.columns(2)

        with col_sort1:

            sort_column = st.selectbox(
                "↕ Sort By",
                filtered_df.columns
            )

        with col_sort2:

            sort_order = st.selectbox(
                "Order",
                [
                    "Descending",
                    "Ascending"
                ]
            )

        ascending = (
            sort_order == "Ascending"
        )

        try:

            filtered_df = filtered_df.sort_values(
                by=sort_column,
                ascending=ascending
            )

        except:
            pass

        st.divider()

        # =============================================
        # RESULT TABLE
        # =============================================

        st.subheader("📋 Shipment Result")

        st.write(
            f"Total Result: {len(filtered_df)}"
        )

        st.dataframe(
            filtered_df,
            use_container_width=True,
            height=600
        )

        st.divider()

        # =============================================
        # QUICK SEARCH ITEM
        # =============================================

        st.subheader(
            "🔥 Quick Search Item"
        )

        search_column = None

        possible_columns = [

            "sku_name",
            "model_name",
            "product_name",
            "item_name"

        ]

        for col in possible_columns:

            if col in filtered_df.columns:

                search_column = col
                break

        if search_column:

            limit_display = st.slider(
                "Jumlah Item Ditampilkan",
                1,
                50,
                10
            )

            for index, row in filtered_df.head(limit_display).iterrows():

                sku = str(
                    row[search_column]
                )

                encoded_sku = quote(sku)

                google_url = (
                    f"https://www.google.com/search?q={encoded_sku}"
                )

                image_url = (
                    f"https://www.google.com/search?tbm=isch&q={encoded_sku}"
                )

                shopee_url = (
                    f"https://shopee.co.id/search?keyword={encoded_sku}"
                )

                tokopedia_url = (
                    f"https://www.tokopedia.com/search?st=product&q={encoded_sku}"
                )

                with st.expander(
                    f"📦 {sku[:120]}"
                ):

                    col1, col2, col3, col4 = st.columns(4)

                    with col1:

                        st.link_button(
                            "🔎 Google",
                            google_url
                        )

                    with col2:

                        st.link_button(
                            "🖼 Images",
                            image_url
                        )

                    with col3:

                        st.link_button(
                            "🛒 Shopee",
                            shopee_url
                        )

                    with col4:

                        st.link_button(
                            "🟢 Tokopedia",
                            tokopedia_url
                        )

        else:

            st.warning(
                "Kolom SKU tidak ditemukan."
            )

        st.divider()

        # =============================================
        # DOWNLOAD
        # =============================================

        csv = filtered_df.to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(

            "⬇ Download CSV",

            csv,

            f"shipment_result_{datetime.now().strftime('%Y%m%d')}.csv",

            "text/csv"

        )

    else:

        st.info(
            "Upload file XLSX / CSV dulu."
        )

# =========================================================
# ANALYTICS
# =========================================================

if menu == "📊 Analytics":

    st.title("📊 Analytics")

    if df is not None:

        df["AI_Category"] = df.astype(str).apply(

            lambda row: detect_category(
                " ".join(map(str, row))
            ),

            axis=1
        )

        st.subheader(
            "🧠 Category Distribution"
        )

        category_counts = (
            df["AI_Category"]
            .value_counts()
        )

        fig, ax = plt.subplots()

        ax.bar(
            category_counts.index,
            category_counts.values
        )

        plt.xticks(rotation=15)

        st.pyplot(fig)

# =========================================================
# AI VISUAL SEARCH
# =========================================================

if menu == "🧠 AI Visual Search":

    st.title(
        "🧠 AI Visual Search"
    )

    uploaded_image = st.file_uploader(
        "Upload Foto Barang",
        type=["jpg", "jpeg", "png"]
    )

    if uploaded_image:

        image = Image.open(uploaded_image)

        st.image(
            image,
            use_container_width=True
        )

        with st.spinner(
            "AI sedang membaca gambar..."
        ):

            image_np = np.array(image)

            results = reader.readtext(
                image_np
            )

            texts = []

            for result in results:

                text = result[1]

                if text.strip():

                    texts.append(text)

            final_text = " ".join(texts)

        st.success(
            "OCR Complete 🔥"
        )

        for txt in texts:

            st.code(txt)

        st.divider()

        category = detect_category(
            final_text
        )

        st.subheader(
            "🧠 AI Category"
        )

        st.success(category)

# =========================================================
# BARCODE SCANNER
# =========================================================

if menu == "📷 Barcode Scanner":

    st.title(
        "📷 Barcode Scanner"
    )

    camera_image = st.camera_input(
        "Ambil Foto Barcode"
    )

    if camera_image:

        image = Image.open(
            camera_image
        )

        st.image(
            image,
            use_container_width=True
        )

        image_np = np.array(image)

        with st.spinner(
            "Scanning..."
        ):

            results = reader.readtext(
                image_np
            )

            texts = []

            for result in results:

                text = result[1]

                if text.strip():

                    texts.append(text)

        if texts:

            st.success(
                "Barcode terbaca 🔥"
            )

            for txt in texts:

                st.code(txt)

# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "🔥 Warehouse AI Super App V8"
)
