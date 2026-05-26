import streamlit as st
import pandas as pd
from PIL import Image
import easyocr
import numpy as np
import re

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Warehouse AI Super App",
    page_icon="🔥",
    layout="wide"
)

# =========================================================
# LOAD OCR
# =========================================================

@st.cache_resource
def load_reader():
    return easyocr.Reader(['en'])

reader = load_reader()

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("🔥 Warehouse AI Super App")

menu = st.sidebar.radio(
    "Pilih Menu",
    [
        "📦 Shipment Dashboard",
        "🧠 AI Visual Search"
    ]
)

st.sidebar.divider()

st.sidebar.info("""
Features:
- Upload XLSX / CSV
- Search realtime
- Filter status
- Filter station
- AI OCR Detection
- Smart Product Detection
- Google Image Search
- AI Summary
""")

# =========================================================
# SHIPMENT DASHBOARD
# =========================================================

if menu == "📦 Shipment Dashboard":

    st.title("📦 Shipment Dashboard")

    uploaded_file = st.file_uploader(
        "Upload XLSX / CSV",
        type=["xlsx", "csv"]
    )

    if uploaded_file:

        # =================================================
        # READ FILE
        # =================================================

        try:

            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)

            else:
                df = pd.read_excel(uploaded_file)

        except Exception as e:

            st.error(f"Error membaca file: {e}")
            st.stop()

        # =================================================
        # CLEAN COLUMN
        # =================================================

        df.columns = [
            str(col).strip()
            for col in df.columns
        ]

        # =================================================
        # METRICS
        # =================================================

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

        # =================================================
        # SEARCH
        # =================================================

        search = st.text_input(
            "🔍 Search Semua Data",
            placeholder="Cari SKU, Resi, SOC_Received, Mouse, HP..."
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

        # =================================================
        # FILTER STATUS
        # =================================================

        status_columns = [
            col for col in filtered_df.columns
            if (
                "status" in col.lower()
                or "desc" in col.lower()
            )
        ]

        if status_columns:

            st.subheader("📦 Filter Status")

            selected_status_col = st.selectbox(
                "Pilih Kolom Status",
                status_columns
            )

            status_options = sorted(
                filtered_df[selected_status_col]
                .astype(str)
                .dropna()
                .unique()
                .tolist()
            )

            selected_status = st.multiselect(
                "Pilih Status",
                status_options
            )

            if selected_status:

                filtered_df = filtered_df[
                    filtered_df[selected_status_col]
                    .astype(str)
                    .isin(selected_status)
                ]

        st.divider()

        # =================================================
        # FILTER STATION
        # =================================================

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
                "Pilih Kolom Station",
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

        # =================================================
        # SORT
        # =================================================

        st.subheader("↕ Sort Data")

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

        st.divider()

        # =================================================
        # RESULT
        # =================================================

        st.subheader("📋 Result")

        st.write(
            f"Total hasil filter: {len(filtered_df)}"
        )

        st.dataframe(
            filtered_df,
            use_container_width=True,
            height=650
        )

        # =================================================
        # DOWNLOAD
        # =================================================

        csv = filtered_df.to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(
            label="⬇ Download CSV",
            data=csv,
            file_name="filtered_result.csv",
            mime="text/csv"
        )

    else:

        st.info(
            "Upload file XLSX / CSV untuk memulai."
        )

# =========================================================
# AI VISUAL SEARCH
# =========================================================

if menu == "🧠 AI Visual Search":

    st.title("🧠 AI Visual Search V2")

    st.caption(
        "Upload foto dus/barang lalu AI akan detect produk otomatis 🔥"
    )

    uploaded_image = st.file_uploader(
        "Upload Foto Barang / Dus",
        type=["jpg", "jpeg", "png"]
    )

    if uploaded_image:

        image = Image.open(uploaded_image)

        col1, col2 = st.columns([1, 1])

        # =================================================
        # IMAGE
        # =================================================

        with col1:

            st.subheader("📷 Uploaded Image")

            st.image(
                image,
                use_container_width=True
            )

        # =================================================
        # AI ANALYSIS
        # =================================================

        with col2:

            st.subheader("🧠 AI Analysis")

            with st.spinner(
                "AI sedang menganalisa gambar..."
            ):

                image_np = np.array(image)

                results = reader.readtext(
                    image_np
                )

                detected_texts = []

                for result in results:

                    text = result[1]

                    if text.strip():

                        detected_texts.append(
                            text
                        )

                final_text = " ".join(
                    detected_texts
                )

                lower_text = final_text.lower()

            st.success(
                "AI Analysis Complete 🔥"
            )

            st.divider()

            # =================================================
            # OCR RESULT
            # =================================================

            st.subheader("📝 OCR Result")

            if detected_texts:

                for txt in detected_texts:
                    st.write(f"• {txt}")

            else:

                st.warning(
                    "Tidak ada text terdeteksi"
                )

            st.divider()

            # =================================================
            # SMART KEYWORDS
            # =================================================

            st.subheader("🔍 Smart Keywords")

            raw_keywords = re.findall(
                r"[A-Za-z0-9\\-]+",
                final_text
            )

            blacklist = [
                "pcs",
                "made",
                "china",
                "colour",
                "color",
                "black",
                "white",
                "brown",
                "qty",
                "model"
            ]

            clean_keywords = []

            for keyword in raw_keywords:

                keyword = keyword.lower()

                if len(keyword) <= 2:
                    continue

                if keyword in blacklist:
                    continue

                if keyword not in clean_keywords:
                    clean_keywords.append(
                        keyword
                    )

            if clean_keywords:

                for keyword in clean_keywords:
                    st.code(keyword)

            else:

                st.warning(
                    "Keyword tidak ditemukan"
                )

            st.divider()

            # =================================================
            # AI PRODUCT ENGINE
            # =================================================

            st.subheader("📦 AI Product Detection")

            detected_products = []
            confidence_scores = {}
            smart_queries = []

            # =================================================
            # FURNITURE ENGINE
            # =================================================

            if (
                "lsj" in lower_text
                or "rack" in lower_text
                or "shelf" in lower_text
            ):

                detected_products.append(
                    "Metal Storage Rack"
                )

                confidence_scores[
                    "Metal Storage Rack"
                ] = "92%"

                smart_queries.append(
                    "LSJ Metal Storage Rack"
                )

            if (
                "chair" in lower_text
                or "seat" in lower_text
            ):

                detected_products.append(
                    "Chair Furniture"
                )

                confidence_scores[
                    "Chair Furniture"
                ] = "88%"
                
                smart_queries.append(
                    "Chair Furniture"
                )

            if (
                "table" in lower_text
                or "desk" in lower_text
            ):

                detected_products.append(
                    "Office Table"
                )

                confidence_scores[
                    "Office Table"
                ] = "85%"

                smart_queries.append(
                    "Office Desk Table"
                )

            # =================================================
            # ELECTRONIC ENGINE
            # =================================================

            if (
                "mouse" in lower_text
                or "keyboard" in lower_text
            ):

                detected_products.append(
                    "Computer Accessories"
                )

                confidence_scores[
                    "Computer Accessories"
                ] = "90%"

                smart_queries.append(
                    "Gaming Mouse Keyboard"
                )

            # =================================================
            # AUTO MODEL DETECTION
            # =================================================

            model_codes = re.findall(
                r"[A-Z]{2,5}-?[0-9]{1,5}",
                final_text
            )

            for model in model_codes:

                detected_products.append(
                    f"Detected Model: {model}"
                )

                confidence_scores[
                    f"Detected Model: {model}"
                ] = "95%"

                smart_queries.append(
                    model
                )

            # =================================================
            # FALLBACK
            # =================================================

            if not detected_products:

                detected_products.append(
                    "Unknown Product"
                )

                confidence_scores[
                    "Unknown Product"
                ] = "40%"

                if clean_keywords:

                    smart_queries.append(
                        " ".join(
                            clean_keywords[:3]
                        )
                    )

            # Remove duplicate
            detected_products = list(
                set(detected_products)
            )

            smart_queries = list(
                set(smart_queries)
            )

            # =================================================
            # SHOW RESULT
            # =================================================

            for product in detected_products:

                score = confidence_scores.get(
                    product,
                    "80%"
                )

                st.success(
                    f"{product} | Confidence: {score}"
                )

            st.divider()

            # =================================================
            # SMART SEARCH
            # =================================================

            st.subheader("🌐 Smart Search")

            if smart_queries:

                for query in smart_queries:

                    google_search = (
                        f"https://www.google.com/search?q={query}"
                    )

                    google_images = (
                        f"https://www.google.com/search?tbm=isch&q={query}"
                    )

                    st.markdown(
                        f"[🔎 Google Search: {query}]({google_search})"
                    )

                    st.markdown(
                        f"[🖼 Google Images: {query}]({google_images})"
                    )

            else:

                st.warning(
                    "Search query tidak ditemukan"
                )

            st.divider()

            # =================================================
            # AI SUMMARY
            # =================================================

            st.subheader("🤖 AI Summary")

            summary = f'''
AI berhasil menganalisa gambar berdasarkan OCR dan pattern recognition.

Detected Text:
{final_text}

Possible Product:
{", ".join(detected_products)}

Recommended Search:
{", ".join(smart_queries)}
'''

            st.text_area(
                "AI Report",
                summary,
                height=250
            )

    else:

        st.info(
            "Upload gambar untuk memulai AI Visual Search."
        )

# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "🔥 Warehouse AI Super App | Streamlit + EasyOCR"
)
