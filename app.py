import re

import pandas as pd
import pdfplumber
import pytesseract
import streamlit as st
from PIL import Image, ImageOps, ImageEnhance

st.set_page_config(
    page_title="HealthDecode",
    page_icon="🩺",
    layout="wide"
)

TESTS = {
    "CBC": {
        "Hemoglobin": {
            "aliases": ["hemoglobin", "haemoglobin", "hgb", "hb"],
            "unit": "g/dL",
            "low": 12.0,
            "high": 17.5,
            "meaning": "Hemoglobin carries oxygen in red blood cells."
        },
        "RBC Count": {
            "aliases": ["rbc count", "red blood cell count",
                        "erythrocyte count"],
            "unit": "million/µL",
            "low": 4.0,
            "high": 6.1,
            "meaning": "RBC count measures red blood cells."
        },
        "WBC Count": {
            "aliases": ["wbc count", "white blood cell count",
                        "total leukocyte count", "tlc"],
            "unit": "cells/µL",
            "low": 4000,
            "high": 11000,
            "meaning": "WBCs participate in immune defence."
        },
        "Platelet Count": {
            "aliases": ["platelet count", "platelets",
                        "thrombocyte count"],
            "unit": "cells/µL",
            "low": 150000,
            "high": 450000,
            "meaning": "Platelets help blood clot."
        }
    },

    "Diabetes": {
        "Fasting Glucose": {
            "aliases": ["fasting blood glucose", "fasting glucose",
                        "fasting blood sugar", "fbs", "fpg"],
            "unit": "mg/dL",
            "low": 70,
            "high": 99,
            "meaning": "Fasting glucose measures blood sugar after fasting."
        },
        "HbA1c": {
            "aliases": ["hba1c", "hb a1c",
                        "glycated hemoglobin"],
            "unit": "%",
            "low": 4.0,
            "high": 5.6,
            "meaning": "HbA1c estimates average blood sugar over about two to three months."
        },
        "Post-meal Glucose": {
            "aliases": ["post prandial glucose", "postprandial glucose",
                        "post meal glucose", "ppbs"],
            "unit": "mg/dL",
            "low": None,
            "high": 140,
            "meaning": "Post-meal glucose measures blood sugar after eating. Timing matters."
        },
        "Random Glucose": {
            "aliases": ["random blood glucose", "random glucose",
                        "random blood sugar", "rbs"],
            "unit": "mg/dL",
            "low": None,
            "high": None,
            "meaning": "Random glucose measures blood sugar regardless of the last meal."
        }
    },

    "Kidney": {
        "Creatinine": {
            "aliases": ["serum creatinine", "creatinine"],
            "unit": "mg/dL",
            "low": 0.5,
            "high": 1.3,
            "meaning": "Creatinine is a waste product used when assessing kidney function."
        },
        "Urea": {
            "aliases": ["blood urea", "serum urea", "urea"],
            "unit": "mg/dL",
            "low": 15,
            "high": 45,
            "meaning": "Urea is a waste product filtered by the kidneys."
        },
        "BUN": {
            "aliases": ["blood urea nitrogen", "bun"],
            "unit": "mg/dL",
            "low": 7,
            "high": 20,
            "meaning": "BUN measures nitrogen from urea in blood."
        },
        "eGFR": {
            "aliases": ["estimated glomerular filtration rate", "egfr"],
            "unit": "mL/min/1.73 m²",
            "low": 60,
            "high": None,
            "meaning": "eGFR estimates how effectively the kidneys filter blood."
        }
    },

    "Liver": {
        "Total Bilirubin": {
            "aliases": ["total bilirubin", "bilirubin total"],
            "unit": "mg/dL",
            "low": 0.1,
            "high": 1.2,
            "meaning": "Bilirubin is a yellow pigment processed by the liver."
        },
        "ALT": {
            "aliases": ["alanine aminotransferase", "sgpt", "alt"],
            "unit": "U/L",
            "low": 7,
            "high": 56,
            "meaning": "ALT is an enzyme that can rise with liver-cell injury."
        },
        "AST": {
            "aliases": ["aspartate aminotransferase", "sgot", "ast"],
            "unit": "U/L",
            "low": 10,
            "high": 40,
            "meaning": "AST is an enzyme found in the liver and other tissues."
        },
        "ALP": {
            "aliases": ["alkaline phosphatase", "alp"],
            "unit": "U/L",
            "low": 44,
            "high": 147,
            "meaning": "ALP is associated with the liver, bile ducts, and bones."
        },
        "Albumin": {
            "aliases": ["serum albumin", "albumin"],
            "unit": "g/dL",
            "low": 3.5,
            "high": 5.0,
            "meaning": "Albumin is a blood protein made by the liver."
        }
    },

    "Lipid Profile": {
        "Total Cholesterol": {
            "aliases": ["total cholesterol", "cholesterol total"],
            "unit": "mg/dL",
            "low": None,
            "high": 200,
            "meaning": "Total cholesterol measures cholesterol carried in the blood."
        },
        "HDL Cholesterol": {
            "aliases": ["hdl cholesterol", "hdl-c", "hdl"],
            "unit": "mg/dL",
            "low": 40,
            "high": None,
            "meaning": "HDL is commonly called good cholesterol."
        },
        "LDL Cholesterol": {
            "aliases": ["ldl cholesterol", "ldl-c", "ldl"],
            "unit": "mg/dL",
            "low": None,
            "high": 100,
            "meaning": "LDL is associated with cholesterol plaque buildup. Targets depend on risk."
        },
        "Triglycerides": {
            "aliases": ["triglycerides", "triglyceride"],
            "unit": "mg/dL",
            "low": None,
            "high": 150,
            "meaning": "Triglycerides are a type of fat in blood."
        }
    },

    "Thyroid": {
        "TSH": {
            "aliases": ["thyroid stimulating hormone", "tsh"],
            "unit": "mIU/L",
            "low": 0.4,
            "high": 4.0,
            "meaning": "TSH signals the thyroid gland to produce hormones."
        },
        "Free T4": {
            "aliases": ["free thyroxine", "free t4", "ft4"],
            "unit": "ng/dL",
            "low": 0.8,
            "high": 1.8,
            "meaning": "Free T4 measures unbound thyroxine in the blood."
        },
        "Total T4": {
            "aliases": ["total thyroxine", "total t4"],
            "unit": "µg/dL",
            "low": 4.5,
            "high": 12.0,
            "meaning": "Total T4 measures bound and unbound thyroxine."
        },
        "Total T3": {
            "aliases": ["total triiodothyronine", "total t3"],
            "unit": "ng/mL",
            "low": 0.8,
            "high": 2.0,
            "meaning": "T3 is a thyroid hormone involved in regulating metabolism."
        }
    }
}


def extract_pdf_text(file):
    file.seek(0)
    with pdfplumber.open(file) as pdf:
        return "\n".join(
            page.extract_text() or ""
            for page in pdf.pages
        )


def extract_image_text(file):
    file.seek(0)
    image = Image.open(file).convert("RGB")
    image = ImageOps.grayscale(image)
    image = ImageEnhance.Contrast(image).enhance(1.8)
    return pytesseract.image_to_string(image)


def parse_values(text, category):
    results = []
    seen = set()

    for line in text.replace("\u00a0", " ").splitlines():
        for test_name, details in TESTS[category].items():
            if test_name in seen:
                continue

            for alias in sorted(
                details["aliases"], key=len, reverse=True
            ):
                pattern = (
                    r"(?<![a-z])" + re.escape(alias.lower())
                    + r"(?![a-z])"
                )

                if not re.search(pattern, line.lower()):
                    continue

                cleaned = re.sub(
                    r"(reference range|normal range|ref\.? range).*$",
                    "",
                    line,
                    flags=re.I
                )

                numbers = re.findall(
                    r"(?<![A-Za-z])[-+]?\d[\d,]*(?:\.\d+)?",
                    cleaned
                )

                if not numbers:
                    continue

                try:
                    value = float(numbers[0].replace(",", ""))
                except ValueError:
                    continue

                results.append({
                    "Test": test_name,
                    "Value": value,
                    "Unit": details["unit"],
                    "Explanation": details["meaning"],
                    "Source line": line.strip()
                })
                seen.add(test_name)
                break

    return results
def interpret(test_name, value, category):
    details = TESTS[category][test_name]
    low = details["low"]
    high = details["high"]

    if category == "Diabetes" and test_name == "HbA1c":
        if value < 5.7:
            return "Within usual screening range"
        elif value < 6.5:
            return "Increased diabetes risk range"
        return "Diabetes-range result; confirmation needed"

    if low is None and high is None:
        return "No automatic classification"

    if low is not None and high is not None:
        if value < low:
            return "Below illustrative guide range"
        elif value > high:
            return "Above illustrative guide range"
        return "Within illustrative guide range"

    if low is not None:
        if value < low:
            return "Below illustrative guide threshold"
        return "At or above illustrative guide threshold"

    if high is not None:
        if test_name == "Total Cholesterol":
            if value >= high:
                return "At or above desirable threshold"
            return "Below desirable threshold"

        if value > high:
            return "Above illustrative guide threshold"
        return "Below illustrative guide threshold"

    return "Needs review"


def get_reference(details):
    low = details["low"]
    high = details["high"]

    if low is not None and high is not None:
        return f"{low:g}–{high:g}"
    elif low is not None:
        return f">= {low:g}"
    elif high is not None:
        return f"< {high:g}"
    return "No automatic range"


# -----------------------------------------------
# HEALTHDECODE WEBSITE
# -----------------------------------------------

st.title("🩺 HealthDecode")
st.subheader("Your medical report, explained simply")

st.write(
    "Upload a laboratory report to identify selected test values "
    "and understand what those tests measure."
)

st.info(
    "This website is an educational prototype, not a "
    "medical diagnostic tool. Automated extraction can misread "
    "numbers, units, and reference ranges. Always verify results "
    "against the original report and consult a healthcare professional."
)

with st.sidebar:
    st.header("Report settings")

    category = st.selectbox(
        "Select report category",
        [
            "CBC",
            "Diabetes",
            "Kidney",
            "Liver",
            "Lipid Profile",
            "Thyroid"
        ]
    )

    st.markdown("---")
    st.write("**Supported reports**")
    st.write("• Complete Blood Count")
    st.write("• Diabetes tests")
    st.write("• Kidney function tests")
    st.write("• Liver function tests")
    st.write("• Lipid profile")
    st.write("• Thyroid tests")


uploaded_file = st.file_uploader(
    "Upload your medical report",
    type=["pdf", "png", "jpg", "jpeg"],
    help="Supported formats: PDF, PNG, JPG and JPEG."
)

st.caption(
    "If the file cannot be read, you can paste text copied "
    "from the original report below."
)

manual_text = st.text_area(
    "Optional: paste report text",
    placeholder=(
        "Example:\n"
        "Hemoglobin 13.5 g/dL\n"
        "WBC Count 7500 cells/uL\n"
        "Platelet Count 250000 cells/uL"
    ),
    height=130
)

extract_button = st.button(
    "Extract and explain report",
    type="primary",
    use_container_width=True
)


if extract_button:
    report_text = ""
    extraction_failed = False

    if manual_text.strip():
        report_text = manual_text.strip()

    elif uploaded_file is None:
        st.warning(
            "Please upload a report or paste report text first."
        )
        extraction_failed = True

    else:
        try:
            if uploaded_file.name.lower().endswith(".pdf"):
                report_text = extract_pdf_text(uploaded_file)

                if not report_text.strip():
                    st.warning(
                        "No selectable text was found in this PDF. "
                        "It may be a scanned document. Copy and paste "
                        "its text, or upload a clear image of the page."
                    )
                    extraction_failed = True

            else:
                report_text = extract_image_text(uploaded_file)

        except Exception as error:
            st.error(
                "The file could not be read. If it is an image, "
                "check whether Tesseract OCR is installed. You can "
                "also paste the report text manually."
            )
            with st.expander("Technical details"):
                st.code(str(error))

            extraction_failed = True

    if not extraction_failed and report_text.strip():

        with st.expander("View extracted report text"):
            st.text(report_text)

        results = parse_values(report_text, category)

        if not results:
            st.warning(
                "No supported test values were identified. "
                "Check the report category or paste clearer text."
            )

        else:
            rows = []

            for result in results:
                test_name = result["Test"]
                value = result["Value"]
                details = TESTS[category][test_name]

                rows.append({
                    "Test": test_name,
                    "Value": value,
                    "Unit": result["Unit"],
                    "Illustrative guide": get_reference(details),
                    "Interpretation": interpret(
                        test_name, value, category
                    ),
                    "Explanation": result["Explanation"],
                    "Source line": result["Source line"]
                })

            st.success(
                f"Found {len(rows)} potentially relevant test values."
            )

            st.subheader("Extracted results")

            st.warning(
                "The detected values are estimates from text parsing. "
                "Review every row against your original laboratory report. "
                "The illustrative guide may not match your laboratory's "
                "reference interval."
            )

            import pandas as pd

            results_df = pd.DataFrame(rows)

            edited_df = st.data_editor(
                results_df,
                use_container_width=True,
                hide_index=True,
                num_rows="dynamic",
                key="healthdecode_editor"
            )

            csv_data = edited_df.to_csv(
                index=False
            ).encode("utf-8")

            st.download_button(
                label="Download results as CSV",
                data=csv_data,
                file_name="healthdecode_results.csv",
                mime="text/csv",
                use_container_width=True
            )

            st.subheader("Understand your results")

            for _, row in edited_df.iterrows():
                with st.expander(
                    f"{row['Test']} — {row['Interpretation']}"
                ):
                    st.write(row["Explanation"])

                    st.write(
                        f"**Extracted value:** {row['Value']} "
                        f"{row['Unit']}"
                    )

                    st.write(
                        f"**Illustrative guide:** "
                        f"{row['Illustrative guide']}"
                    )

                    st.caption(
                        "This comparison is educational only. "
                        "Interpretation depends on the laboratory's "
                        "reference interval, units, age, clinical "
                        "history and other factors."
                    )


st.divider()

st.caption(
    "HealthDecode | Biomedical Engineering Prototype"
)

st.caption(
    "This application does not diagnose medical conditions or "
    "recommend treatment. The current parser may mistake a nearby "
    "number or reference-range value for the actual test result."
)
