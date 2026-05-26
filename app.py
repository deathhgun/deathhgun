import streamlit as st
import pandas as pd
from PIL import Image
import easyocr
import numpy as np
import re

st.set_page_config(
    page_title="Warehouse Super App",
    layout="wide"
)

# SIDEBAR
menu = st.sidebar.selectbox(
    "Pilih Menu",
    [
        "📦 Shipment Dashboard",
        "🧠 AI Visual Search"
    ]
)

# =========================
# SHIPMENT DASHBOARD
# =========================

if menu == "📦 Shipment Dashboard":

    st.title("📦 Shipment Dashboard")

    uploaded_file = st.file_uploader(
        "Upload XLSX / CSV",
        type=["xlsx", "csv"]
    )

    if uploaded_file:

        # READ FILE
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        st.success("File berhasil diupload!")

        # SEARCH
        search = st.text_input(
            "🔍 Search Semua Data",
            placeholder="Cari HP, Mouse, SKU, Resi..."
        )

        filtered_df = df.copy()

        if search:
            mask = filtered_df.astype(str).apply(
                lambda row: row.str.contains(
                    search,
                    case=False
                ).any(),
                axis=1
            )

            filtered_df = filtered_df[mask]

        # FILTER STATION
        station_columns = [
            col for col in filtered_df.columns
            if "station" in col.lower()
        ]

        if station_columns:

            selected_station_col = st.selectbox(
                "Pilih Kolom Station",
                station_columns
            )

            station_options = filtered_df[
                selected_station_col
            ].astype(str).unique()

            selected_station = st.multiselect(
                "Filter Station",
                station_options
            )

            if selected_station:
                filtered_df = filtered_df[
                    filtered_df[selected_station_col]
                    .astype(str)
                    .isin(selected_station)
                ]

        # SORT
        sort_column = st.selectbox(
            "Sort By",
            filtered_df.columns
        )

        ascending = st.checkbox("Ascending")

        filtered_df = filtered_df.sort_values(
            by=sort_column,
            ascending=ascending
        )

        # METRICS
        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Total Data",
                len(filtered_df)
            )

        with col2:
            st.metric(
                "Total Kolom",
                len(filtered_df.columns)
            )

        st.divider()

        # TABLE
        st.dataframe(
            filtered_df,
            use_container_width=True,
            height=600
        )

        # DOWNLOAD
        csv = filtered_df.to_csv(index=False).encode("utf-8")

        st.download_button(
            "⬇ Download Result",
            csv,
            "filtered_result.csv",
            "text/csv"
        )

# =========================
# AI VISUAL SEARCH
# =========================

elif menu == "🧠 AI Visual Search":

    st.title("🧠 AI Visual Search")

    uploaded_image = st.file_uploader(
        "Upload Foto Dus / Barang",
        type=["jpg", "jpeg", "png"]
    )

    if uploaded_image:

        image = Image.open(uploaded_image)

        col1, col2 = st.columns(2)

        with col1:
            st.image(
                image,
                caption="Uploaded Image",
                use_container_width=True
            )

        with col2:

            with st.spinner(
                "AI sedang membaca gambar..."
            ):

                reader = easyocr.Reader(['en'])

                image_np = np.array(image)

                results = reader.readtext(image_np)

                detected_texts = []

                for result in results:
                    detected_texts.append(result[1])

                final_text = " ".join(
                    detected_texts
                )

                st.success(
                    "AI Detection Selesai!"
                )

                st.subheader(
                    "📝 Detected Text"
                )

                if detected_texts:
                    for txt in detected_texts:
                        st.write(f"• {txt}")
                else:
                    st.warning(
                        "Tidak ada text terdeteksi"
                    )

                st.divider()

                st.subheader(
                    "🔍 AI Keywords"
                )

                keywords = re.findall(
                    r'[A-Za-z0-9\\-]+',
                    final_text
                )

                unique_keywords = list(
                    set(keywords)
                )

                for keyword in unique_keywords:
                    if len(keyword) > 2:
                        st.code(keyword)

                st.divider()

                st.subheader(
                    "📦 Possible Product"
                )

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

                if not possible_products:
                    possible_products.append(
                        "Unknown Product"
                    )

                for item in possible_products:
                    st.success(item)

                st.divider()

                st.subheader(
                    "🌐 Suggested Search"
                )

                for keyword in unique_keywords[:5]:

                    search_url = (
                        f\"https://www.google.com/search?q={keyword}\"
                    )

                    st.markdown(
                        f\"[🔎 Search {keyword}]({search_url})\"
                    )

    else:
        st.info(
            "Upload gambar untuk memulai AI detection."
        )
