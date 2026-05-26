import streamlit as st
import pandas as pd
from PIL import Image
import easyocr
import numpy as np
import re
import matplotlib.pyplot as plt
from rapidfuzz import fuzz

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="🔥 Warehouse AI Super App V5",
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

st.sidebar.title("🔥 Warehouse AI Super App V5")

menu = st.sidebar.radio(
    "Pilih Menu",
    [
        "📦 Shipment Dashboard",
        "📊 Analytics Dashboard",
        "🧠 AI Visual Search",
        "📷 Barcode / Label Scanner"
    ]
)

st.sidebar.divider()

st.sidebar.success("System Online ✅")

# =========================================================
# GLOBAL FILE UPLOAD
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

        df.columns = [
            str(col).strip()
            for col in df.columns
        ]

    except Exception as e:

        st.error(f"Error membaca file: {e}")

# =========================================================
# SMART SEARCH FUNCTION
# =========================================================

def smart_search_dataframe(dataframe, search):

    if not search:
        return dataframe

    shortcuts = {
        "cd": "celana dalam",
        "hp": "handphone",
        "rak": "rack",
        "meja": "table",
        "kursi": "chair",
        "lemari": "cabinet",
        "tv": "television"
    }

    search_text = search.lower()

    for short, full in shortcuts.items():

        if short in search_text:

            search_text = search_text.replace(
                short,
                full
            )

    def smart_search(row):

        row_text = " ".join(
            row.astype(str)
        ).lower()

        # =====================================
        # EXACT SEARCH
        # =====================================

        if search_text in row_text:
            return True

        # =====================================
        # FUZZY SEARCH
        # =====================================

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
# SHIPMENT DASHBOARD
# =========================================================

if menu == "📦 Shipment Dashboard":

    st.title("📦 Shipment Dashboard")

    if df is not None:

        # =================================================
        # METRICS
        # =================================================

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Total Rows",
                len(df)
            )

        with col2:
            st.metric(
                "Total Columns",
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

        with col4:

            duplicate_count = df.duplicated().sum()

            st.metric(
                "Duplicates",
                duplicate_count
            )

        st.divider()

        # =================================================
        # SMART SEARCH
        # =================================================

        search = st.text_input(
            "🔍 Smart Search",
            placeholder="Cari SKU, Resi, CD Shaka, HP Samsung..."
        )

        filtered_df = smart_search_dataframe(
            df,
            search
        )

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

        st.subheader("📋 Shipment Result")

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
            "⬇ Download CSV",
            csv,
            "filtered_result.csv",
            "text/csv"
        )

    else:

        st.info(
            "Upload file XLSX / CSV dulu di sidebar."
        )

# =========================================================
# ANALYTICS DASHBOARD
# =========================================================

if menu == "📊 Analytics Dashboard":

    st.title("📊 Analytics Dashboard")

    if df is not None:

        # =============================================
        # STATUS ANALYTICS
        # =============================================

        status_columns = [
            col for col in df.columns
            if (
                "status" in col.lower()
                or "desc" in col.lower()
            )
        ]

        if status_columns:

            selected_status_col = status_columns[0]

            st.subheader("📦 Status Distribution")

            status_counts = (
                df[selected_status_col]
                .astype(str)
                .value_counts()
                .head(10)
            )

            fig, ax = plt.subplots()

            ax.bar(
                status_counts.index,
                status_counts.values
            )

            plt.xticks(rotation=45)

            st.pyplot(fig)

        # =============================================
        # STATION ANALYTICS
        # =============================================

        station_columns = [
            col for col in df.columns
            if (
                "station" in col.lower()
                or "origin" in col.lower()
                or "dest" in col.lower()
            )
        ]

        if station_columns:

            selected_station_col = station_columns[0]

            st.subheader("📍 Station Distribution")

            station_counts = (
                df[selected_station_col]
                .astype(str)
                .value_counts()
                .head(10)
            )

            fig2, ax2 = plt.subplots()

            ax2.bar(
                station_counts.index,
                station_counts.values
            )

            plt.xticks(rotation=45)

            st.pyplot(fig2)

    else:

        st.info(
            "Upload file XLSX / CSV dulu di sidebar."
        )

# =========================================================
# AI VISUAL SEARCH
# =========================================================

if menu == "🧠 AI Visual Search":

    st.title("🧠 AI Visual Search")

    uploaded_image = st.file_uploader(
        "Upload Foto Barang",
        type=["jpg", "jpeg", "png"]
    )

    if uploaded_image:

        image = Image.open(uploaded_image)

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

                lower_text = final_text.lower()

            st.success(
                "AI Analysis Complete 🔥"
            )

            st.subheader("📝 OCR Result")

            if texts:

                for txt in texts:
                    st.code(txt)

            else:

                st.warning(
                    "Tidak ada text terdeteksi"
                )

            st.divider()

            # =========================================
            # PRODUCT DETECTION
            # =========================================

            st.subheader("📦 AI Product Detection")

            detected_products = []

            if (
                "rack" in lower_text
                or "shelf" in lower_text
            ):

                detected_products.append(
                    "Metal Rack"
                )

            if "chair" in lower_text:

                detected_products.append(
                    "Chair Furniture"
                )

            if "table" in lower_text:

                detected_products.append(
                    "Table Furniture"
                )

            if "mouse" in lower_text:

                detected_products.append(
                    "Computer Accessories"
                )

            model_codes = re.findall(
                r"[A-Z]{2,5}-?[0-9]{1,5}",
                final_text
            )

            for model in model_codes:

                detected_products.append(
                    f"Model: {model}"
                )

            if not detected_products:

                detected_products.append(
                    "Unknown Product"
                )

            detected_products = list(
                set(detected_products)
            )

            for product in detected_products:

                st.success(product)

            st.divider()

            # =========================================
            # SMART SEARCH
            # =========================================

            st.subheader("🌐 Smart Search")

            search_query = (
                " ".join(detected_products)
            )

            google_search = (
                f"https://www.google.com/search?q={search_query}"
            )

            google_images = (
                f"https://www.google.com/search?tbm=isch&q={search_query}"
            )

            st.markdown(
                f"[🔎 Google Search]({google_search})"
            )

            st.markdown(
                f"[🖼 Google Images]({google_images})"
            )

    else:

        st.info(
            "Upload gambar untuk memulai."
        )

# =========================================================
# BARCODE / LABEL SCANNER
# =========================================================

if menu == "📷 Barcode / Label Scanner":

    st.title("📷 Barcode / Label Scanner")

    st.caption(
        "Gunakan kamera HP untuk scan label / barcode"
    )

    camera_image = st.camera_input(
        "Ambil Foto Barcode / Label"
    )

    if camera_image:

        image = Image.open(camera_image)

        st.image(
            image,
            use_container_width=True
        )

        image_np = np.array(image)

        with st.spinner(
            "Membaca barcode..."
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
                "Barcode berhasil dibaca 🔥"
            )

            for txt in texts:
                st.code(txt)

            combined = " ".join(texts)

            st.divider()

            # =========================================
            # AWB DETECTION
            # =========================================

            st.subheader("📦 AWB Detection")

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

                    # =================================
                    # AUTO SEARCH SHIPMENT
                    # =================================

                    if df is not None:

                        shipment_result = smart_search_dataframe(
                            df,
                            awb
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

            st.divider()

            # =========================================
            # GOOGLE SEARCH
            # =========================================

            st.subheader("🌐 Smart Search")

            google_search = (
                f"https://www.google.com/search?q={combined}"
            )

            st.markdown(
                f"[🔎 Search Barcode]({google_search})"
            )

        else:

            st.warning(
                "Barcode tidak terbaca"
            )

# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "🔥 Warehouse AI Super App V5"
)
