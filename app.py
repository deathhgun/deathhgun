# ======================================================
# AI VISUAL SEARCH V2
# ======================================================

elif menu == "🧠 AI Visual Search":

    st.title("🧠 AI Visual Search V2")

    st.caption(
        "Upload foto dus/barang lalu AI akan detect produk secara otomatis"
    )

    uploaded_image = st.file_uploader(
        "Upload Foto",
        type=["jpg", "jpeg", "png"]
    )

    if uploaded_image:

        image = Image.open(uploaded_image)

        col1, col2 = st.columns([1, 1])

        # ==========================================
        # IMAGE
        # ==========================================

        with col1:

            st.subheader("📷 Uploaded Image")

            st.image(
                image,
                use_container_width=True
            )

        # ==========================================
        # AI DETECTION
        # ==========================================

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

            # ==========================================
            # OCR RESULT
            # ==========================================

            st.subheader("📝 OCR Result")

            if detected_texts:

                for txt in detected_texts:
                    st.write(f"• {txt}")

            else:

                st.warning(
                    "Tidak ada text terdeteksi"
                )

            st.divider()

            # ==========================================
            # SMART KEYWORDS
            # ==========================================

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
                "qty"
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

            # ==========================================
            # AI PRODUCT ENGINE
            # ==========================================

            st.subheader("📦 AI Product Detection")

            detected_products = []

            confidence_scores = {}

            smart_queries = []

            # ======================================
            # FURNITURE ENGINE
            # ======================================

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
                "desk" in lower_text
                or "table" in lower_text
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

            # ======================================
            # ELECTRONIC ENGINE
            # ======================================

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

            # ======================================
            # AUTO MODEL DETECTION
            # ======================================

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

            # ======================================
            # FALLBACK
            # ======================================

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

            # Remove duplicates
            detected_products = list(
                set(detected_products)
            )

            smart_queries = list(
                set(smart_queries)
            )

            # ======================================
            # SHOW PRODUCTS
            # ======================================

            for product in detected_products:

                score = confidence_scores.get(
                    product,
                    "80%"
                )

                st.success(
                    f"{product} | Confidence: {score}"
                )

            st.divider()

            # ==========================================
            # SMART SEARCH
            # ==========================================

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

            # ==========================================
            # FINAL AI SUMMARY
            # ==========================================

            st.subheader("🤖 AI Summary")

            summary = f'''
AI mendeteksi kemungkinan produk berdasarkan OCR dan pattern recognition.

Detected Text:
{final_text}

Possible Product:
{", ".join(detected_products)}

Recommended Search:
{", ".join(smart_queries)}
'''

            st.text_area(
                "AI Analysis Report",
                summary,
                height=250
            )

    else:

        st.info(
            "Upload gambar untuk memulai AI Visual Search."
        )
