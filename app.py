import streamlit as st
import pandas as pd
from PIL import Image
import easyocr
import numpy as np
import re
import matplotlib.pyplot as plt
from rapidfuzz import fuzz
from datetime import datetime

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="🔥 Warehouse AI Super App V7",
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

.stDataFrame {
    border-radius: 10px;
}

.block-container {
    padding-top: 1rem;
}

.metric-box {
    background: #1E1E1E;
    padding: 10px;
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

st.sidebar.title("🔥 Warehouse AI Super App V7")

menu = st.sidebar.radio(
    "Menu",
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
# SMART SEARCH ENGINE
# =========================================================

def smart_search_dataframe(dataframe, search):

    if not search:
        return dataframe

    shortcuts = {

        "cd": "celana dalam",
        "hp": "handphone",
        "rak": "rack",
        "lemari": "cabinet",
        "tv": "television",
        "kaos": "baju",
        "sepatu": "sneakers"

    }

    search_text = search.lower()

    # SHORTCUT
    for short, full in shortcuts.items():

        if short in search_text:

            search_text = search_text.replace(
                short,
                full
            )

    # SEARCH
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
# AI CATEGORY DETECTOR
# =========================================================

def detect_category(text):

    text = str(text).lower()

    categories = {

        "👕 Fashion": [

            "celana",
            "baju",
            "kaos",
            "hoodie",
            "sepatu",
            "fashion",
            "tas",
            "kemeja",
            "rok"

        ],

        "🍳 Rumah Tangga": [

            "rice cooker",
            "kompor",
            "piring",
            "gelas",
            "dapur",
            "blender",
            "miyako"

        ],

        "📱 Elektronik": [

            "hp",
            "handphone",
            "samsung",
            "iphone",
            "laptop",
            "keyboard",
            "mouse",
            "monitor",
            "tv"

        ],

        "🪑 Furniture": [

            "rack",
            "rak",
            "lemari",
            "meja",
            "kursi",
            "cabinet",
            "sofa"

        ],

        "🧸 Mainan": [

            "lego",
            "boneka",
            "mainan",
            "toy"

        ],

        "💄 Beauty": [

            "skincare",
            "serum",
            "parfum",
            "makeup"

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
        # AUTO CATEGORY
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

            duplicate_count = (
                df.duplicated().sum()
            )

            st.metric(
                "Duplicates",
                duplicate_count
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
                "Cari SKU, Resi, "
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

        st.subheader(
            "🧠 AI Category Filter"
        )

        categories = sorted(
            filtered_df["AI_Category"]
            .unique()
        )

        selected_categories = st.multiselect(
            "Pilih Category",
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
                "Sort By",
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
        # RESULT
        # =============================================

        st.subheader("📋 Shipment Result")

        st.write(
            f"Total Result: {len(filtered_df)}"
        )

        st.dataframe(
            filtered_df,
            use_container_width=True,
            height=650
        )

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
            "Upload XLSX / CSV dulu."
        )

# =========================================================
# ANALYTICS
# =========================================================

if menu == "📊 Analytics":

    st.title("📊 Analytics Dashboard")

    if df is not None:

        df["AI_Category"] = df.astype(str).apply(

            lambda row: detect_category(
                " ".join(map(str, row))
            ),

            axis=1
        )

        # CATEGORY CHART

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

        st.divider()

        # STATUS CHART

        status_columns = [

            col for col in df.columns

            if (
                "status" in col.lower()
                or "desc" in col.lower()
            )

        ]

        if status_columns:

            selected_status_col = (
                status_columns[0]
            )

            st.subheader(
                "📦 Status Distribution"
            )

            status_counts = (

                df[selected_status_col]
                .astype(str)
                .value_counts()
                .head(10)

            )

            fig2, ax2 = plt.subplots()

            ax2.bar(
                status_counts.index,
                status_counts.values
            )

            plt.xticks(rotation=45)

            st.pyplot(fig2)

    else:

        st.info(
            "Upload file dulu."
        )

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

        image = Image.open(
            uploaded_image
        )

        col1, col2 = st.columns(2)

        with col1:

            st.image(
                image,
                use_container_width=True
            )

        with col2:

            with st.spinner(
                "AI sedang menganalisa..."
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
                "AI Analysis Complete 🔥"
            )

            st.subheader(
                "📝 OCR Result"
            )

            if texts:

                for txt in texts:

                    st.code(txt)

            else:

                st.warning(
                    "Tidak ada text terdeteksi"
                )

            st.divider()

            detected_category = detect_category(
                final_text
            )

            st.subheader(
                "🧠 AI Category"
            )

            st.success(
                detected_category
            )

            st.divider()

            # GOOGLE SEARCH

            google_search = (
                f"https://www.google.com/search?q={final_text}"
            )

            google_images = (
                f"https://www.google.com/search?tbm=isch&q={final_text}"
            )

            st.markdown(
                f"[🔎 Google Search]({google_search})"
            )

            st.markdown(
                f"[🖼 Google Images]({google_images})"
            )

# =========================================================
# BARCODE SCANNER
# =========================================================

if menu == "📷 Barcode Scanner":

    st.title(
        "📷 Barcode Scanner"
    )

    camera_image = st.camera_input(
        "Ambil Foto Barcode / Label"
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
                "Label berhasil dibaca 🔥"
            )

            for txt in texts:

                st.code(txt)

            combined = " ".join(texts)

            st.divider()

            # CATEGORY

            detected_category = detect_category(
                combined
            )

            st.subheader(
                "🧠 AI Category"
            )

            st.success(
                detected_category
            )

            st.divider()

            # AWB DETECTOR

            st.subheader(
                "📦 AWB Detection"
            )

            awb_patterns = [

                r"SPXID[0-9]+",
                r"NA[0-9]+"

            ]

            found_awb = []

            for pattern in awb_patterns:

                matches = re.findall(
                    pattern,
                    combined
                )

                found_awb.extend(matches)

            if found_awb:

                for awb in found_awb:

                    st.success(
                        f"Detected AWB: {awb}"
                    )

                    if df is not None:

                        shipment_result = (
                            smart_search_dataframe(
                                df,
                                awb
                            )
                        )

                        if not shipment_result.empty:

                            st.subheader(
                                "📋 Shipment Match"
                            )

                            st.dataframe(
                                shipment_result,
                                use_container_width=True
                            )

            else:

                st.warning(
                    "AWB tidak ditemukan"
                )

# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "🔥 Warehouse AI Super App V7"
)
