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

# Custom CSS for better styling
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
    </style>
""", unsafe_allow_html=True)

# Title
st.title("📊 Practical Harmonic Analysis Calculator")
st.markdown("---")

# Sidebar for configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Number of data points
    num_points = st.number_input("Number of Data Points", min_value=1, max_value=100, value=12, step=1)
    
    st.markdown("---")
    st.subheader("Custom Functions")
    custom_functions = []
    
    num_custom = st.number_input("Number of Custom Functions", min_value=0, max_value=5, value=0, step=1)
    
    for i in range(int(num_custom)):
        st.markdown(f"**Custom Function {i+1}**")
        func_name = st.text_input(f"Function Name {i+1}", f"custom_{i+1}", key=f"name_{i}")
        func_expr = st.text_input(
            f"Expression {i+1} (use 'y', 'x_rad', 'x_deg')", 
            "y * np.sin(x_rad)", 
            key=f"expr_{i}",
            help="Examples: y * np.sin(x_rad), y * x_deg, y**2"
        )
        custom_functions.append((func_name, func_expr))

# Main content area
st.header("📝 Input Data")

# Initialize session state for data
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame({
        'x (degrees)': [i * 30.0 for i in range(int(num_points))],
        'y': [0.0] * int(num_points)
    })

# Adjust dataframe size if num_points changed
if len(st.session_state.data) != num_points:
    current_data = st.session_state.data.copy()
    new_data = pd.DataFrame({
        'x (degrees)': [i * 30.0 for i in range(int(num_points))],
        'y': [0.0] * int(num_points)
    })
    
    # Copy existing data
    copy_len = min(len(current_data), int(num_points))
    new_data.iloc[:copy_len, 1] = current_data.iloc[:copy_len, 1]  # Copy only y values
    st.session_state.data = new_data

# Data editor
st.info("💡 Enter your y values below (X values increment by 30° automatically):")

# Use a copy to avoid state issues
display_data = st.session_state.data.copy()

edited_data = st.data_editor(
    display_data,
    use_container_width=True,
    num_rows="fixed",
    hide_index=True,
    key="data_editor",
    column_config={
        "x (degrees)": st.column_config.NumberColumn(
            "x (degrees)",
            disabled=True,
            help="Automatically increments by 30°"
        ),
        "y": st.column_config.NumberColumn(
            "y",
            help="Enter your y values here"
        )
    }
)

# Only update session state if y values actually changed
if not edited_data['y'].equals(st.session_state.data['y']):
    st.session_state.data = edited_data

# Quick fill options
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("🔢 Fill X (30° increments)"):
        st.session_state.data['x (degrees)'] = [i * 30.0 for i in range(int(num_points))]
        st.rerun()

with col2:
    if st.button("📈 Fill Sample Y (sin wave)"):
        x_vals = st.session_state.data['x (degrees)'].values
        st.session_state.data['y'] = np.sin(np.radians(x_vals))
        st.rerun()

with col3:
    if st.button("🗑️ Clear Y Values"):
        st.session_state.data['y'] = [0.0] * int(num_points)
        st.rerun()

# Function selection on main page
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

# Calculate button
st.markdown("---")
if st.button("🧮 Calculate Harmonic Analysis", type="primary", use_container_width=True):
    
    # Create results dataframe
    results_df = st.session_state.data.copy()
    
    # Convert degrees to radians
    x_deg = results_df['x (degrees)'].values
    x_rad = np.radians(x_deg)
    y = results_df['y'].values
    
    # Calculate selected functions
    if calc_ysinx:
        results_df['y·sin(x)'] = y * np.sin(x_rad)
    
    if calc_ycosx:
        results_df['y·cos(x)'] = y * np.cos(x_rad)
    
    if calc_ysin2x:
        results_df['y·sin(2x)'] = y * np.sin(2 * x_rad)
    
    if calc_ycos2x:
        results_df['y·cos(2x)'] = y * np.cos(2 * x_rad)
    
    if calc_ysin3x:
        results_df['y·sin(3x)'] = y * np.sin(3 * x_rad)
    
    if calc_ycos3x:
        results_df['y·cos(3x)'] = y * np.cos(3 * x_rad)
    
    # Calculate custom functions
    for func_name, func_expr in custom_functions:
        if func_name and func_expr:
            try:
                # Create safe evaluation environment
                safe_dict = {
                    'y': y,
                    'x_rad': x_rad,
                    'x_deg': x_deg,
                    'np': np,
                    'sin': np.sin,
                    'cos': np.cos,
                    'tan': np.tan,
                    'exp': np.exp,
                    'log': np.log,
                    'sqrt': np.sqrt
                }
                result = eval(func_expr, {"__builtins__": {}}, safe_dict)
                results_df[func_name] = result
            except Exception as e:
                st.error(f"Error evaluating custom function '{func_name}': {str(e)}")
    
    # Display results
    st.markdown("---")
    st.header("📊 Results")
    
    # Format the dataframe for display
    styled_df = results_df.style.format("{:.6f}").set_properties(**{
        'text-align': 'center',
        'font-size': '13px',
        'border': '1px solid #ddd'
    }).set_table_styles([
        {'selector': 'th', 'props': [
            ('background-color', '#2E86AB'),
            ('color', 'white'),
            ('font-weight', 'bold'),
            ('text-align', 'center'),
            ('padding', '10px')
        ]},
        {'selector': 'td', 'props': [
            ('padding', '8px')
        ]},
        {'selector': 'tr:hover', 'props': [
            ('background-color', '#f5f5f5')
        ]}
    ])
    
    st.dataframe(styled_df, use_container_width=True, height=400, hide_index=True)
    
    # Calculate and display sums directly below the table
    st.markdown("### 📊 Column Sums")
    
    # Create sums row with empty first column
    sums_data = {'x (degrees)': ['']}  # Empty string instead of 'SUM'
    for col in results_df.columns:
        if col != 'x (degrees)':
            sums_data[col] = [results_df[col].sum()]
    
    sums_df = pd.DataFrame(sums_data)
    
    styled_sums = sums_df.style.format({
        col: "{:.6f}" for col in sums_df.columns if col != 'x (degrees)'
    }).set_properties(**{
        'text-align': 'center',
        'font-size': '15px',
        'font-weight': 'bold',
        'background-color': '#FFE082',
        'color': '#000000',
        'border': '2px solid #FF6F00',
        'padding': '12px'
    }).set_table_styles([
        {'selector': 'th', 'props': [
            ('background-color', '#FF6F00'),
            ('color', 'white'),
            ('font-weight', 'bold'),
            ('text-align', 'center'),
            ('padding', '12px'),
            ('font-size', '14px'),
            ('border', '2px solid #FF6F00')
        ]},
        {'selector': 'td', 'props': [
            ('border', '2px solid #FF6F00'),
            ('background-color', '#FFE082')
        ]},
        {'selector': 'table', 'props': [
            ('border-collapse', 'separate'),
            ('border-spacing', '0'),
            ('border', '3px solid #FF6F00'),
            ('box-shadow', '0 4px 6px rgba(0,0,0,0.1)')
        ]}
    ])
    
    st.dataframe(styled_sums, use_container_width=True, hide_index=True)
    
    # Fourier coefficients calculation
    st.markdown("---")
    st.subheader("🔢 Fourier Coefficients")
    
    n = len(y)
    a0 = np.sum(y) / n
    
    coeffs_data = {
        'Coefficient': ['a₀'],
        'Value': [a0]
    }
    
    if calc_ycosx:
        a1 = 2 * np.sum(y * np.cos(x_rad)) / n
        coeffs_data['Coefficient'].append('a₁')
        coeffs_data['Value'].append(a1)
    
    if calc_ysinx:
        b1 = 2 * np.sum(y * np.sin(x_rad)) / n
        coeffs_data['Coefficient'].append('b₁')
        coeffs_data['Value'].append(b1)
    
    if calc_ycos2x:
        a2 = 2 * np.sum(y * np.cos(2 * x_rad)) / n
        coeffs_data['Coefficient'].append('a₂')
        coeffs_data['Value'].append(a2)
    
    if calc_ysin2x:
        b2 = 2 * np.sum(y * np.sin(2 * x_rad)) / n
        coeffs_data['Coefficient'].append('b₂')
        coeffs_data['Value'].append(b2)
    
    coeffs_df = pd.DataFrame(coeffs_data)
    
    styled_coeffs = coeffs_df.style.format({'Value': '{:.6f}'}).set_properties(**{
        'text-align': 'center',
        'font-size': '14px',
        'padding': '10px'
    }).set_table_styles([
        {'selector': 'th', 'props': [
            ('background-color', '#2E86AB'),
            ('color', 'white'),
            ('font-weight', 'bold'),
            ('text-align', 'center'),
            ('padding', '10px')
        ]}
    ])
    
    st.dataframe(styled_coeffs, use_container_width=True)
    
    # Download option
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
    </div>
""", unsafe_allow_html=True)
