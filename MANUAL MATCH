import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Shipment Dashboard",
    layout="wide"
)

st.title("📦 Shipment Dashboard")
st.caption("Upload file XLSX atau CSV lalu search & filter shipment")

uploaded_file = st.file_uploader(
    "Upload File",
    type=["xlsx", "csv"]
)

if uploaded_file:
    try:
        # Read file
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        st.success(f"File berhasil diupload: {uploaded_file.name}")

        # Clean column names
        df.columns = [str(col).strip() for col in df.columns]

        # Dashboard metrics
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total Data", len(df))

        with col2:
            st.metric("Total Kolom", len(df.columns))

        with col3:
            st.metric("Unique Shipment", df.iloc[:,0].nunique())

        st.divider()

        # Search box
        search = st.text_input(
            "🔍 Search",
            placeholder="Cari HP, Mouse, Kalawat DC, dll..."
        )

        filtered_df = df.copy()

        # Global search
        if search:
            mask = filtered_df.astype(str).apply(
                lambda row: row.str.contains(search, case=False).any(),
                axis=1
            )

            filtered_df = filtered_df[mask]

        # Station filter
        station_columns = [
            col for col in filtered_df.columns
            if 'station' in col.lower()
            or 'origin' in col.lower()
            or 'destination' in col.lower()
        ]

        if station_columns:
            selected_station_col = st.selectbox(
                "📍 Pilih Kolom Station",
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
                "Filter Station",
                station_options
            )

            if selected_station:
                filtered_df = filtered_df[
                    filtered_df[selected_station_col]
                    .astype(str)
                    .isin(selected_station)
                ]

        st.divider()

        # Sort section
        col_sort1, col_sort2 = st.columns(2)

        with col_sort1:
            sort_column = st.selectbox(
                "Sort By",
                filtered_df.columns.tolist()
            )

        with col_sort2:
            sort_order = st.selectbox(
                "Urutan",
                ["Descending", "Ascending"]
            )

        ascending = sort_order == "Ascending"

        filtered_df = filtered_df.sort_values(
            by=sort_column,
            ascending=ascending
        )

        # Final metrics
        st.subheader("📋 Hasil Filter")
        st.write(f"Total hasil: {len(filtered_df)}")

        # Display dataframe
        st.dataframe(
            filtered_df,
            use_container_width=True,
            height=600
        )

        # Download button
        csv = filtered_df.to_csv(index=False).encode('utf-8')

        st.download_button(
            label="⬇ Download Hasil Filter",
            data=csv,
            file_name="filtered_shipment.csv",
            mime="text/csv"
        )

    except Exception as e:
        st.error(f"Terjadi error: {e}")

else:
    st.info("Silakan upload file XLSX atau CSV untuk memulai.")

st.divider()
st.caption("Made with Streamlit 🚀")
