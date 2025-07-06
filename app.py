import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Page config with custom theme colors
st.set_page_config(
    page_title="Explaina – Your Data, Explained",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# === Custom CSS ===
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .block-container {
        padding-top: 2rem;
    }
    h1, h2, h3 {
        color: #222831;
    }
    .st-emotion-cache-1cypcdb {
        padding: 1rem;
        background: #ffffff;
        border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

# === Header ===
st.markdown("<h1 style='text-align: center;'>📊 Explaina – Automated EDA + Insight Generator</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Upload a CSV file and let Explaina uncover patterns, visuals, and smart insights ✨</p>", unsafe_allow_html=True)

# === Sidebar Upload ===
st.sidebar.title("📁 Upload Data")
uploaded_file = st.sidebar.file_uploader("📂 Choose a CSV file", type=["csv"])

# === Initialize session history ===
if "history" not in st.session_state:
    st.session_state.history = []

# === Process Uploaded File ===
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    # Save to session history (limit 5)
    if uploaded_file.name not in [entry["filename"] for entry in st.session_state.history]:
        st.session_state.history.insert(0, {
            "filename": uploaded_file.name,
            "shape": df.shape,
            "columns": df.columns.tolist(),
            "nulls": df.isnull().sum().to_dict()
        })
        if len(st.session_state.history) > 5:
            st.session_state.history.pop()

    st.sidebar.success("✅ Upload successful")

    # === Main Tabs ===
    tab1, tab2, tab3 = st.tabs(["🔍 Overview", "📊 Visualizations", "💡 Insights"])

    with tab1:
        st.subheader("👀 Dataset Preview")
        st.dataframe(df)

        st.subheader("📌 Basic Information")
        st.write(f"📐 Shape: {df.shape[0]} rows × {df.shape[1]} columns")
        st.write("🧾 Columns:", df.columns.tolist())
        st.write("❗ Null values per column:")
        st.write(df.isnull().sum())

    with tab2:
        st.subheader("📊 Visualizations")

        numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
        if len(numeric_cols) >= 2:
            chart_type = st.selectbox("📋 Choose Chart Type", ["Scatter Plot", "Histogram", "Box Plot", "Pair Plot"])

            col1 = st.selectbox("📈 Select X-axis", numeric_cols)
            col2 = st.selectbox("📉 Select Y-axis", numeric_cols, index=1)

            if chart_type == "Scatter Plot":
                st.write(f"📌 Scatter Plot: {col1} vs {col2}")
                fig, ax = plt.subplots()
                sns.scatterplot(x=df[col1], y=df[col2], ax=ax)
                st.pyplot(fig)

                # === Auto Caption Logic ===
                corr = df[[col1, col2]].corr().iloc[0, 1]
                if abs(corr) > 0.7:
                    strength = "strong"
                elif abs(corr) > 0.4:
                    strength = "moderate"
                elif abs(corr) > 0.2:
                    strength = "weak"
                else:
                    strength = "very weak or no"
                direction = "positive" if corr > 0 else "negative" if corr < 0 else "no"
                st.markdown(f"📝 **Caption**: There is a {strength} {direction} correlation between **{col1}** and **{col2}** (correlation = `{corr:.2f}`).")

            elif chart_type == "Histogram":
                st.write(f"📌 Histogram for {col1}")
                fig, ax = plt.subplots()
                sns.histplot(df[col1], kde=True, ax=ax)
                st.pyplot(fig)

            elif chart_type == "Box Plot":
                st.write(f"📌 Box Plot for {col1}")
                fig, ax = plt.subplots()
                sns.boxplot(y=df[col1], ax=ax)
                st.pyplot(fig)

            elif chart_type == "Pair Plot":
                st.write("📌 Pair Plot")
                fig = sns.pairplot(df[numeric_cols[:4]])
                st.pyplot(fig)
        else:
            st.warning("⚠️ Not enough numeric columns to generate visualizations.")

    with tab3:
        st.subheader("💡 Generated Insights")
        st.write("🧠 Analyzing key patterns in your data...")

        insights = []
        for col in df.columns:
            if df[col].dtype in [np.int64, np.float64]:
                mean = df[col].mean()
                std = df[col].std()
                if mean > 1000:
                    insights.append(f"📈 Column **{col}** has a high average value: {mean:.2f}")
                if std > mean:
                    insights.append(f"⚠️ Column **{col}** has high variability.")

        if insights:
            for ins in insights:
                st.markdown(ins)
        else:
            st.info("🤷‍♀️ No strong insights found. Try a bigger or more varied dataset.")

        # === Report Generation ===
        st.markdown("---")
        st.subheader("📝 Download Report")

        report_lines = [
            f"📁 Filename: {uploaded_file.name}",
            f"📐 Shape: {df.shape[0]} rows × {df.shape[1]} columns",
            f"🧾 Columns: {', '.join(df.columns)}",
            "❗ Null Values Per Column:"
        ]
        nulls = df.isnull().sum()
        for col, val in nulls.items():
            report_lines.append(f"  - {col}: {val}")
        report_lines.append("\n💡 Insights:")
        if insights:
            for i in insights:
                report_lines.append(f"- {i.replace('**', '')}")
        else:
            report_lines.append("- No strong insights found.")

        report_text = "\n".join(report_lines)

        st.download_button(
            label="📥 Download .txt Report",
            data=report_text,
            file_name=f"{uploaded_file.name.split('.')[0]}_report.txt",
            mime="text/plain"
        )

else:
    st.warning("📤 Please upload a CSV file to begin analysis.")

# === Sidebar Session History ===
st.sidebar.markdown("---")
st.sidebar.subheader("🕘 Previous Sessions")

if st.session_state["history"]:
    for item in st.session_state["history"]:
        with st.sidebar.expander(f"📁 {item['filename']}"):
            st.write(f"📐 Shape: {item['shape'][0]} rows × {item['shape'][1]} columns")
            st.write("🧾 Columns:", item['columns'])
            nulls = {k: v for k, v in item["nulls"].items() if v > 0}
            st.write("❗ Nulls:", nulls if nulls else "No missing values")
else:
    st.sidebar.write("No past session stored.")
