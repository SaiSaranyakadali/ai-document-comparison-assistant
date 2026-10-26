import os
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv

from document_reader import extract_pdf_text, PDFReadError
from comparison import compare_documents, ComparisonError
from report_generator import create_docx_report


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

load_dotenv()

st.set_page_config(
    page_title="AI Document Comparison Assistant",
    page_icon="📄",
    layout="wide",
)

# Initialize session state
if "comparison_result" not in st.session_state:
    st.session_state.comparison_result = None

if "history" not in st.session_state:
    st.session_state.history = []

if "upload_version" not in st.session_state:
    st.session_state.upload_version = 0

if "file_names" not in st.session_state:
    st.session_state.file_names = ("", "")

if "page_counts" not in st.session_state:
    st.session_state.page_counts = (0, 0)


# --------------------------------------------------
# SESSION ACTIONS
# --------------------------------------------------

def start_new_chat():
    """Start a new comparison without deleting history."""
    st.session_state.comparison_result = None
    st.session_state.file_names = ("", "")
    st.session_state.page_counts = (0, 0)
    st.session_state.upload_version += 1


def clear_current_chat():
    """Clear the current comparison and uploaded documents."""
    start_new_chat()


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:
    st.title("📄 Document Assistant")
    st.caption("Compare PDFs with AI")

    st.divider()

    if st.button("➕ New Chat", use_container_width=True):
        start_new_chat()
        st.rerun()

    if st.button("🧹 Clear Chat", use_container_width=True):
        clear_current_chat()
        st.rerun()

    st.divider()

    st.subheader("🕘 History")

    history = st.session_state.history

    if history:
        history_options = list(range(len(history) - 1, -1, -1))

        selected_history = st.selectbox(
            "Previous comparisons",
            options=history_options,
            format_func=lambda i: history[i]["title"],
            key="history_selection",
        )

        if st.button(
            "📂 Open Comparison",
            use_container_width=True,
        ):
            item = history[selected_history]

            st.session_state.comparison_result = item["result"]
            st.session_state.file_names = item["file_names"]
            st.session_state.page_counts = item["page_counts"]

            # Clear old upload widgets when opening history.
            st.session_state.upload_version += 1

            st.rerun()

        if st.button(
            "🗑️ Clear History",
            use_container_width=True,
        ):
            st.session_state.history = []
            st.session_state.comparison_result = None
            st.session_state.file_names = ("", "")
            st.session_state.page_counts = (0, 0)
            st.session_state.upload_version += 1
            st.rerun()

    else:
        st.caption("No previous comparisons yet.")

    st.divider()

    st.caption(
        "Your history is stored in the current session. "
        "It may be lost when the session ends."
    )


# --------------------------------------------------
# MAIN PAGE
# --------------------------------------------------

st.title("📄 AI Document Comparison Assistant")

st.write(
    "Upload two PDF documents to generate individual summaries, "
    "identify similarities and differences, and compare important details."
)

st.info(
    "This tool provides informational comparisons only. "
    "It is not legal advice or a compliance decision-maker."
)


# --------------------------------------------------
# PDF UPLOAD
# --------------------------------------------------

upload_version = st.session_state.upload_version

col_a, col_b = st.columns(2)

with col_a:
    file_a = st.file_uploader(
        "📘 Document A (PDF)",
        type=["pdf"],
        key=f"pdf_a_{upload_version}",
    )

with col_b:
    file_b = st.file_uploader(
        "📗 Document B (PDF)",
        type=["pdf"],
        key=f"pdf_b_{upload_version}",
    )


# --------------------------------------------------
# PDF TEXT EXTRACTION AND PREVIEW
# --------------------------------------------------

def show_preview(upload, label):
    if upload is None:
        return None, 0

    st.caption(
        f"**{label}:** {upload.name} · "
        f"{upload.size:,} bytes"
    )

    try:
        text, pages = extract_pdf_text(upload.getvalue())

        st.caption(
            f"Extracted {len(text):,} characters "
            f"from {pages} page(s)."
        )

        with st.expander(f"Preview {label} extracted text"):
            preview = text[:1800]

            if len(text) > 1800:
                preview += "..."

            st.text(preview)

        return text, pages

    except PDFReadError as error:
        st.error(f"{label}: {error}")
        return None, 0


text_a, pages_a = show_preview(file_a, "Document A")
text_b, pages_b = show_preview(file_b, "Document B")


# --------------------------------------------------
# COMPARE DOCUMENTS
# --------------------------------------------------

if st.button(
    "🔍 Compare Documents",
    type="primary",
    use_container_width=True,
):
    st.session_state.comparison_result = None

    if not file_a or not file_b:
        st.error(
            "Please upload both Document A and Document B."
        )

    elif not os.getenv("GEMINI_API_KEY"):
        st.error(
            "GEMINI_API_KEY is missing. "
            "Please configure your Gemini API key in the .env file."
        )

    elif not text_a or not text_b:
        st.error(
            "Both PDFs must contain readable text. "
            "No comparison was started."
        )

    elif (
        len(text_a) > 90000
        or len(text_b) > 90000
        or len(text_a) + len(text_b) > 140000
    ):
        st.error(
            "The documents are too long for this version. "
            "Maximum: 90,000 characters per document and "
            "140,000 characters combined."
        )

    else:
        try:
            with st.spinner(
                "Analyzing PDFs and generating comparison..."
            ):
                api_key = os.getenv("GEMINI_API_KEY")

                model_name = os.getenv(
                    "GEMINI_MODEL",
                    "gemini-3.6-flash",
                )

                result = compare_documents(
                    text_a,
                    text_b,
                    file_a.name,
                    file_b.name,
                    api_key,
                    model_name,
                )

                file_names = (file_a.name, file_b.name)
                page_counts = (pages_a, pages_b)

                st.session_state.comparison_result = result
                st.session_state.file_names = file_names
                st.session_state.page_counts = page_counts

                # Save the completed comparison in session history.
                history_item = {
                    "title": (
                        f"{file_a.name} vs {file_b.name} "
                        f"· {datetime.now().strftime('%d %b %H:%M')}"
                    ),
                    "result": result,
                    "file_names": file_names,
                    "page_counts": page_counts,
                }

                st.session_state.history.append(history_item)

            st.success("Comparison completed successfully!")

        except ComparisonError as error:
            st.error(f"Comparison failed: {error}")

        except Exception as error:
            st.error(
                f"An unexpected error occurred: {error}"
            )


# --------------------------------------------------
# DISPLAY RESULTS
# --------------------------------------------------

result = st.session_state.comparison_result

if result:

    st.divider()
    st.header("📊 Comparison Results")

    tab_a, tab_b, tab_sim, tab_diff, tab_details, tab_conclusion = (
        st.tabs(
            [
                "Summary A",
                "Summary B",
                "Similarities",
                "Differences",
                "Key Details",
                "Conclusion & Limits",
            ]
        )
    )

    # Document A summary
    with tab_a:
        st.subheader(result["document_a"]["file_name"])
        st.write(result["document_a"]["summary"])

    # Document B summary
    with tab_b:
        st.subheader(result["document_b"]["file_name"])
        st.write(result["document_b"]["summary"])

    # Similarities
    with tab_sim:
        st.subheader("Similarities")

        items = result.get("similarities", [])

        if items:
            for item in items:
                st.markdown(f"- {item}")
        else:
            st.write(
                "No supported similarities were identified."
            )

    # Differences
    with tab_diff:
        st.subheader("Differences")

        items = result.get("differences", [])

        if items:
            for item in items:
                st.markdown(f"- {item}")
        else:
            st.write(
                "No supported differences were identified."
            )

    # Key details
    with tab_details:
        st.subheader("Key Details Comparison")

        details = result.get("key_details", [])

        if details:
            rows = [
                {
                    "Detail": item.get("detail", ""),
                    "Document A": item.get("document_a", ""),
                    "Document B": item.get("document_b", ""),
                    "Change / Note": item.get("change", ""),
                }
                for item in details
            ]

            st.dataframe(
                rows,
                use_container_width=True,
                hide_index=True,
            )

        else:
            st.write("No key details were returned.")

    # Conclusion and limitations
    with tab_conclusion:
        st.subheader("Overall Conclusion")

        st.write(
            result.get(
                "overall_conclusion",
                "Not found in the provided text.",
            )
        )

        st.subheader("Limitations")

        limitations = result.get("limitations", [])

        if limitations:
            for item in limitations:
                st.markdown(f"- {item}")
        else:
            st.write("No additional limitations were reported.")

    # --------------------------------------------------
    # DOWNLOAD REPORT
    # --------------------------------------------------

    st.divider()
    st.subheader("📥 Download Report")

    try:
        report = create_docx_report(result)

        st.download_button(
            label="⬇️ Download Comparison Report (DOCX)",
            data=report,
            file_name="document_comparison_report.docx",
            mime=(
                "application/vnd.openxmlformats-officedocument."
                "wordprocessingml.document"
            ),
            type="primary",
            use_container_width=True,
        )

    except Exception as error:
        st.error(
            f"Could not generate the comparison report: {error}"
        )


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "📄 AI Document Comparison Assistant · "
    "Upload text-based PDFs for the best results. "
    "Scanned PDF OCR is not included."
)
