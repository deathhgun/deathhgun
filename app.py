import streamlit as st
import pandas as pd
from PIL import Image
import easyocr
import numpy as np
import re

# ============================================
# CONFIG
# ============================================

st.set_page_config(
    page_title="Warehouse Super App",
    page_icon="📦",
    layout="wide"
)

# ============================================
# CACHE OCR
# ============================================

@st.cache_resource
def load_ocr():
    return easyocr.Reader(['en'])

reader = load_ocr()

# ============================================
# SIDEBAR
# ============================================

st.sidebar.title("📦 Warehouse Super App")

menu = st.sidebar.radio(
    "Pilih Menu",
    [
        "📦 Shipment Dashboard",
        "🧠 AI Visual Search"
    ]
)

st.sidebar.divider()

st.sidebar.info(
    """
    Features:
    - Upload XLSX / CSV
    - Search realtime
    - Filter station
    - Sort data
    - AI OCR Detection
    - AI Keyword Generator
    """
)

# ============================================
# SHIPMENT DASHBOARD
# ============================================

if menu == "📦 Shipment Dashboard":

    st.title("📦 Shipment Dashboard")

    uploaded_file = st.file_uploader(
        "Upload File XLSX / CSV",
        type=["xlsx", "csv"]
    )

    if uploaded_file:

        # ====================================
        # READ FILE
        # ====================================

        try:

            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)

        except Exception as e:
            st.error(f"Gagal membaca file: {e}")
            st.stop()

        # ====================================
        # CLEAN COLUMN
        # ====================================

        df.columns = [
            str(col).strip()
            for col in df.columns
        ]

        st.success("File berhasil diupload!")

        # ====================================
        # METRICS
        # ====================================

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Total Data",
                len(df)
            )

        with col2:
            st.metric(
                "Total Kolom",
                len(df.columns)
            )

        with col3:

            try:
                unique_shipment = df.iloc[:, 0].nunique()
            except:
                unique_shipment = 0

            st.metric(
                "Unique Shipment",
                unique_shipment
            )

        st.divider()

        # ====================================
        # SEARCH
        # ====================================

        search = st.text_input(
            "🔍 Search Semua Data",
            placeholder="Cari SKU, Resi, Mouse, HP, Station..."
        )

        filtered_df = df.copy()

        if search:

            mask = filtered_df.astype(str).apply(
                lambda row: row.str.contains(
                    search,
                    case=False,
                    na=False
                ).any(),
                axis=1
            )

            filtered_df = filtered_df[mask]

        # ====================================
        # FILTER STATION
        # ====================================

        station_columns = [
            col for col in filtered_df.columns
            if (
                "station" in col.lower()
                or "origin" in col.lower()
                or "dest" in col.lower()
            )
        ]

        if station_columns:

            st.subheader("📍 Filter Station")

            selected_station_col = st.selectbox(
                "Pilih Kolom",
                station_columns
            )

            station_options = sorted(
                filtered_df[selected_station_col]
                .astype(str)
                .dropna()
                .unique()
                .tolist()
            )

            selected_station = st.multiselect(
                "Pilih Station",
                station_options
            )

            if selected_station:

                filtered_df = filtered_df[
                    filtered_df[selected_station_col]
                    .astype(str)
                    .isin(selected_station)
                ]

        st.divider()

        # ====================================
        # SORT
        # ====================================

        col_sort1, col_sort2 = st.columns(2)

        with col_sort1:

            sort_column = st.selectbox(
                "Sort By",
                filtered_df.columns
            )

        with col_sort2:

            sort_order = st.selectbox(
                "Urutan",
                [
                    "Descending",
                    "Ascending"
                ]
            )

        ascending = sort_order == "Ascending"

        try:

            filtered_df = filtered_df.sort_values(
                by=sort_column,
                ascending=ascending
            )

        except:
            pass

        # ====================================
        # RESULT
        # ====================================

        st.subheader("📋 Result")

        st.write(
            f"Total hasil filter: {len(filtered_df)}"
        )

        st.dataframe(
            filtered_df,
            use_container_width=True,
            height=600
        )

        # ====================================
        # DOWNLOAD
        # ====================================

        csv = filtered_df.to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(
            label="⬇ Download Result CSV",
            data=csv,
            file_name="filtered_result.csv",
            mime="text/csv"
        )

    else:

        st.info(
            "Upload file XLSX / CSV untuk memulai."
        )

# ============================================
# AI VISUAL SEARCH
# ============================================

elif menu == "🧠 AI Visual Search":

    st.title("🧠 AI Visual Search")

    uploaded_image = st.file_uploader(
        "Upload Foto Dus / Barang",
        type=["jpg", "jpeg", "png"]
    )

    if uploaded_image:

        image = Image.open(uploaded_image)

        col1, col2 = st.columns([1, 1])

        # ====================================
        # IMAGE
        # ====================================

        with col1:

            st.subheader("📷 Uploaded Image")

            st.image(
                image,
                use_container_width=True
            )

        # ====================================
        # OCR
        # ====================================

        with col2:

            st.subheader("🧠 AI Detection")

            with st.spinner(
                "AI sedang membaca gambar..."
            ):

                try:

                    image_np = np.array(image)

                    results = reader.readtext(
                        image_np
                    )

                    detected_texts = []

                    for result in results:

                        text = result[1]

                        if text.strip():
                            detected_texts.append(text)

                    final_text = " ".join(
                        detected_texts
                    )

                    st.success(
                        "Detection selesai!"
                    )

                except Exception as e:

                    st.error(
                        f"OCR Error: {e}"
                    )

                    st.stop()

            # ====================================
            # DETECTED TEXT
            # ====================================

            st.subheader("📝 Detected Text")

            if detected_texts:

                for txt in detected_texts:
                    st.write(f"• {txt}")

            else:

                st.warning(
                    "Tidak ada text terdeteksi"
                )

            st.divider()

            # ====================================
            # KEYWORDS
            # ====================================

            st.subheader("🔍 AI Keywords")

            keywords = re.findall(
                r"[A-Za-z0-9\\-]+",
                final_text
            )

            unique_keywords = []

            for keyword in keywords:

                if (
                    len(keyword) > 2
                    and keyword.lower()
                    not in unique_keywords
                ):

                    unique_keywords.append(
                        keyword.lower()
                    )

            if unique_keywords:

                for keyword in unique_keywords:
                    st.code(keyword)

            else:

                st.warning(
                    "Keyword tidak ditemukan"
                )

            st.divider()

            # ====================================
            # PRODUCT DETECTION
            # ====================================

            st.subheader("📦 Possible Product")

            lower_text = final_text.lower()

            possible_products = []

            if "lsj" in lower_text:
                possible_products.append(
                    "Metal Rack / Shelf"
                )

            if "black" in lower_text:
                possible_products.append(
                    "Black Furniture"
                )

            if "pcs" in lower_text:
                possible_products.append(
                    "Bulk Package"
                )

            if "chair" in lower_text:
                possible_products.append(
                    "Chair Furniture"
                )

            if "table" in lower_text:
                possible_products.append(
                    "Table Furniture"
                )

            if not possible_products:

                possible_products.append(
                    "Unknown Product"
                )

            for item in possible_products:
                st.success(item)

            st.divider()

            # ====================================
            # SEARCH LINK
            # ====================================

            st.subheader("🌐 Suggested Search")

            if unique_keywords:

                for keyword in unique_keywords[:5]:

                    search_url = (
                        f"https://www.google.com/search?q={keyword}"
                    )

                    st.markdown(
                        f"[🔎 Search {keyword}]({search_url})"
                    )

            else:

                st.warning(
                    "Tidak ada keyword untuk search"
                )

    else:

        st.info(
            "Upload gambar untuk memulai AI detection."
        )

# ============================================
# FOOTER
# ============================================

st.divider()

st.caption(
    "🚀 Warehouse Super App | Streamlit + OCR"
)
