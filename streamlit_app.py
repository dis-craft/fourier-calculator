import streamlit as st 
import pandas as pd
import numpy as np
import math

# Page configuration
st.set_page_config(
    page_title="Fourier Series Calculator",
    page_icon="📊",
    layout="wide"
)

# Custom CSS for better styling + remove +/- spinners for number inputs by using text inputs style
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stDataFrame {
        font-size: 14px;
    }
    h1 {
        color: #2E86AB;
        text-align: center;
        margin-bottom: 2rem;
    }
    h3 {
        color: #A23B72;
        margin-top: 2rem;
    }
    .sum-row {
        background-color: #f0f2f6;
        font-weight: bold;
    }

    /* text inputs styling to look like boxes and avoid +/- spinners */
    .stTextInput>div>div>input {
        padding: 8px 10px !important;
        border-radius: 6px !important;
        border: 1px solid #d0d7de !important;
        font-size: 14px !important;
    }
    .stTextInput>div>label { display:none; } /* hide duplicate labels in compact layout */
    </style>
""", unsafe_allow_html=True)

# Title
st.title("📊 Practical Harmonic Analysis Calculator")
st.markdown("---")

# Configuration on main page
st.header("⚙️ Configuration")

col_config1, col_config2 = st.columns([1, 2])

with col_config1:
    # Number of data points
    num_points = int(st.number_input(
        "Number of Data Points(m value)",
        min_value=1,
        max_value=100,
        value=12,
        step=1
    ))

with col_config2:
    st.markdown("")  # Spacer

st.markdown("---")

# ---------------- Input area replaced with text-input logic (keeps everything else same) ----------------

# Initialize / preserve per-row keys (do NOT pass value= to widgets)
if "n_prev" not in st.session_state:
    st.session_state.n_prev = 0

# preserve existing values; create new keys for added rows
if num_points != st.session_state.n_prev:
    for i in range(num_points):
        x_key = f"x_input_{i}"
        y_key = f"y_input_{i}"
        if x_key not in st.session_state:
            # default x: 30° increments
            st.session_state[x_key] = f"{i * 30.0:.6f}"
        if y_key not in st.session_state:
            # default y: 0
            st.session_state[y_key] = "0.000000"
    st.session_state.n_prev = num_points

st.header("📝 Input Table ")
st.info("Type numeric values of x,y into the boxes.")

# Table header (removed serial number column)
col1, col2 = st.columns([1, 1])
col1.markdown("**x (degrees)**")
col2.markdown("**y**")

# Render inputs (text_input) and avoid passing 'value' argument to prevent overwriting user's typing.
# Use session_state keys for initial content and to store typed values live.
for i in range(num_points):
    c1, c2 = st.columns([1, 1])
    x_key = f"x_input_{i}"
    y_key = f"y_input_{i}"

    # Ensure keys exist (they do from init above). Use label_visibility collapsed to keep layout compact.
    c1.text_input("", key=x_key, label_visibility="collapsed", placeholder="e.g. 0.0")
    c2.text_input("", key=y_key, label_visibility="collapsed", placeholder="e.g. 0.0")

# Helpers to parse text inputs to floats safely
def parse_float_safe(s):
    try:
        s = str(s).replace(",", ".").strip()
        if s == "" or s.lower() in ["nan", "none", "-"]:
            return 0.0
        return float(s)
    except Exception:
        return 0.0

# Quick fill buttons
c1, c2 = st.columns(2)
with c1:
    if st.button("🔢 Fill X (30° increments)"):
        for i in range(num_points):
            st.session_state[f"x_input_{i}"] = f"{i * 30.0:.6f}"
        st.experimental_rerun()
with c2:
    if st.button("🗑️ Clear Y Values"):
        for i in range(num_points):
            st.session_state[f"y_input_{i}"] = "0.000000"
        st.experimental_rerun()

# Collect parsed arrays
x_vals = np.array([parse_float_safe(st.session_state.get(f"x_input_{i}", "0")) for i in range(num_points)], dtype=float)
y_vals = np.array([parse_float_safe(st.session_state.get(f"y_input_{i}", "0")) for i in range(num_points)], dtype=float)
x_rad = np.radians(x_vals)

# Show live sums for input columns right away (so user sees sum without pressing calculate)
# col_s1, col_s2 = st.columns([1, 1])
# with col_s1:
#     st.metric("Sum of x (degrees)", f"{x_vals.sum():.6f}")
# with col_s2:
#     st.metric("Sum of y", f"{y_vals.sum():.6f}")

# ---------------- Function selection ----------------

st.markdown("---")
st.subheader("🔧 Select Functions to Calculate")

col_f1, col_f2, col_f3, col_f4, col_f5, col_f6 = st.columns(6)

with col_f1:
    calc_ysinx = st.checkbox("y·sin(x)", value=True)
with col_f2:
    calc_ycosx = st.checkbox("y·cos(x)", value=True)
with col_f3:
    calc_ysin2x = st.checkbox("y·sin(2x)", value=True)
with col_f4:
    calc_ycos2x = st.checkbox("y·cos(2x)", value=True)
with col_f5:
    calc_ysin3x = st.checkbox("y·sin(3x)", value=False)
with col_f6:
    calc_ycos3x = st.checkbox("y·cos(3x)", value=False)

# Custom Functions section
st.markdown("")
with st.expander("➕ Custom Functions (Optional)", expanded=False):
    num_custom = int(st.number_input(
        "Number of Custom Functions",
        min_value=0,
        max_value=5,
        value=0,
        step=1
    ))
    
    custom_functions = []
    for i in range(num_custom):
        col_name, col_expr = st.columns(2)
        with col_name:
            func_name = st.text_input(
                f"Function Name {i+1}",
                f"custom_{i+1}",
                key=f"name_{i}"
            )
        with col_expr:
            func_expr = st.text_input(
                f"Expression {i+1} (use 'y', 'x_rad', 'x_deg')",
                "y * np.sin(x_rad)",
                key=f"expr_{i}",
                help="Examples: y * np.sin(x_rad), y * x_deg, y**2"
            )
        custom_functions.append((func_name, func_expr))

# ---------------- Calculate button ----------------

st.markdown("---")
if st.button("🧮 Calculate Harmonic Analysis", type="primary", use_container_width=True):

    # Build dataframe from current inputs
    x_deg = x_vals.copy()
    y = y_vals.copy()
    x_rad = np.radians(x_deg)

    results_df = pd.DataFrame({
        "x (degrees)": x_deg,
        "y": y
    })

    # Calculate selected functions
    if calc_ysinx:
        results_df["y·sin(x)"] = y * np.sin(x_rad)

    if calc_ycosx:
        results_df["y·cos(x)"] = y * np.cos(x_rad)

    if calc_ysin2x:
        results_df["y·sin(2x)"] = y * np.sin(2 * x_rad)

    if calc_ycos2x:
        results_df["y·cos(2x)"] = y * np.cos(2 * x_rad)

    if calc_ysin3x:
        results_df["y·sin(3x)"] = y * np.sin(3 * x_rad)

    if calc_ycos3x:
        results_df["y·cos(3x)"] = y * np.cos(3 * x_rad)

    # Custom functions
    for func_name, func_expr in custom_functions:
        if func_name and func_expr:
            try:
                safe_dict = {
                    "y": y,
                    "x_rad": x_rad,
                    "x_deg": x_deg,
                    "np": np,
                    "sin": np.sin,
                    "cos": np.cos,
                    "tan": np.tan,
                    "exp": np.exp,
                    "log": np.log,
                    "sqrt": np.sqrt,
                }
                result = eval(func_expr, {"__builtins__": {}}, safe_dict)
                results_df[func_name] = result
            except Exception as e:
                st.error(f"Error evaluating custom function '{func_name}': {str(e)}")

    # ------------- Results table -------------

    st.markdown("---")
    st.header("📊 Results")

    styled_df = (
        results_df.style.format("{:.6f}")
        .set_properties(
            **{
                "text-align": "center",
                "font-size": "13px",
                "border": "1px solid #ddd",
            }
        )
        .set_table_styles(
            [
                {
                    "selector": "th",
                    "props": [
                        ("background-color", "#2E86AB"),
                        ("color", "white"),
                        ("font-weight", "bold"),
                        ("text-align", "center"),
                        ("padding", "10px"),
                    ],
                },
                {
                    "selector": "td",
                    "props": [
                        ("padding", "8px"),
                    ],
                },
                {
                    "selector": "tr:hover",
                    "props": [
                        ("background-color", "#f5f5f5"),
                    ],
                },
            ]
        )
    )

    st.dataframe(styled_df, use_container_width=True, height=400, hide_index=True)

    # ------------- Column sums -------------
    st.markdown("### 📊 Column Sums")

    # Include x sum as well now
    sums_data = {"x (degrees)": [results_df["x (degrees)"].sum()]}
    for col in results_df.columns:
        if col != "x (degrees)":
            sums_data[col] = [results_df[col].sum()]

    sums_df = pd.DataFrame(sums_data)

    styled_sums = (
        sums_df.style.format(
            {col: "{:.6f}" for col in sums_df.columns if col != "x (degrees)"}
        )
        .set_properties(
            **{
                "text-align": "center",
                "font-size": "15px",
                "font-weight": "bold",
                "background-color": "#FFE082",
                "color": "#000000",
                "border": "2px solid #FF6F00",
                "padding": "12px",
            }
        )
        .set_table_styles(
            [
                {
                    "selector": "th",
                    "props": [
                        ("background-color", "#FF6F00"),
                        ("color", "white"),
                        ("font-weight", "bold"),
                        ("text-align", "center"),
                        ("padding", "12px"),
                        ("font-size", "14px"),
                        ("border", "2px solid #FF6F00"),
                    ],
                },
                {
                    "selector": "td",
                    "props": [
                        ("border", "2px solid #FF6F00"),
                        ("background-color", "#FFE082"),
                    ],
                },
                {
                    "selector": "table",
                    "props": [
                        ("border-collapse", "separate"),
                        ("border-spacing", "0"),
                        ("border", "3px solid #FF6F00"),
                        ("box-shadow", "0 4px 6px rgba(0,0,0,0.1)"),
                    ],
                },
            ]
        )
    )

    st.dataframe(styled_sums, use_container_width=True, hide_index=True)

    # ------------- Fourier coefficients -------------

    st.markdown("---")
    st.subheader("🔢 Fourier Coefficients(Might be incorrect.)")

    n = len(y)
    a0 = np.sum(y) / n

    coeffs_data = {"Coefficient": ["a₀"], "Value": [a0]}

    if calc_ycosx:
        a1 = 2 * np.sum(y * np.cos(x_rad)) / n
        coeffs_data["Coefficient"].append("a₁")
        coeffs_data["Value"].append(a1)

    if calc_ysinx:
        b1 = 2 * np.sum(y * np.sin(x_rad)) / n
        coeffs_data["Coefficient"].append("b₁")
        coeffs_data["Value"].append(b1)

    if calc_ycos2x:
        a2 = 2 * np.sum(y * np.cos(2 * x_rad)) / n
        coeffs_data["Coefficient"].append("a₂")
        coeffs_data["Value"].append(a2)

    if calc_ysin2x:
        b2 = 2 * np.sum(y * np.sin(2 * x_rad)) / n
        coeffs_data["Coefficient"].append("b₂")
        coeffs_data["Value"].append(b2)

    coeffs_df = pd.DataFrame(coeffs_data)

    styled_coeffs = (
        coeffs_df.style.format({"Value": "{:.6f}"})
        .set_properties(
            **{
                "text-align": "center",
                "font-size": "14px",
                "padding": "10px",
            }
        )
        .set_table_styles(
            [
                {
                    "selector": "th",
                    "props": [
                        ("background-color", "#2E86AB"),
                        ("color", "white"),
                        ("font-weight", "bold"),
                        ("text-align", "center"),
                        ("padding", "10px"),
                    ],
                }
            ]
        )
    )

    st.dataframe(styled_coeffs, use_container_width=True)

    # ------------- Download option -------------
    st.markdown("---")
    csv = results_df.to_csv(index=False)
    st.download_button(
        label="📥 Download Results as CSV",
        data=csv,
        file_name="harmonic_analysis_results.csv",
        mime="text/csv",
        use_container_width=True
    )

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p><strong>Practical Harmonic Analysis Calculator</strong></p>
        <p>For Fourier series analysis and harmonic component calculation</p>
        <p style='margin-top: 15px; font-size: 14px;'>
            By <a href='https://www.linkedin.com/in/srikar-t-118581286/' target='_blank' style='color: #2E86AB; text-decoration: none; font-weight: bold;'>Srikar</a>
        </p>
    </div>
""", unsafe_allow_html=True)

