import pandas as pd
import streamlit as st
from conectsupabase import *

st.set_page_config(layout="wide")

def insertsp(file_excel):
    cols = [0, 2, 4, 5, 6, 7]
    data = pd.read_excel(file_excel, usecols=cols, skiprows=1)
    data = data.iloc[:-4]
    data.columns = ['Store_code', 'Item_code', 'Item_desc', 'LOCATOR', 'BARCODE', 'Qty']
    data['BARCODE'] = data['BARCODE'].astype(str)
    data['Qty'] = data['Qty'].astype(float)
    data['Item_desc'] = data['Item_desc'].str[18:]

    #print(data.info())
    #print(data.head())
    # Convert DataFrame to JSON format
    data_json = data.to_dict(orient='records')
    if insert_Data('stock_mex', data_json):
        return True
    
def getsp(item_barcode, item_code):
    inp = item_barcode.strip()
    it = item_code.strip()
    

    if it != '':
        condition = f' "Item_code" = \'{it}\' '
        df = getdata('stock_mex', "*", condition)
    else:
        columns = "*"
        condition = f' "BARCODE" = \'{inp}\' '
        print(f"Condition: {condition}")
        df_ucc = getdata('stock_mex', columns, condition)
        #print(df_ucc)
        it = df_ucc['Item_code'].iloc[0] if not df_ucc.empty else ''
        if not df_ucc.empty:
            columns = "*"
            condition = f' "Item_code" = \'{it}\' '
            print(f"Condition: {condition}")
            df = getdata('stock_mex', columns, condition)
        else:
            # If no matching barcode, return error message
            return "Sai Barcode hoac Item code"
    if df is None or df.empty:
        return "Sai Barcode hoac Item code"
    # If df is empty after query, return error message
    return df

def main():


    st.markdown(
        '<h1 style="color:#1976d2; font-weight:bold;">KIEM TRA KHO MEX</h1>',
        unsafe_allow_html=True
    )
    #st.title("KIEM TRA KHO MEX")
    data = pd.DataFrame()

    uploaded_file = st.file_uploader("Chọn file Excel mới để xem dữ liệu", type=["xls", "xlsx"])
    if uploaded_file is not None:
        
        delete_Data('stock_mex', {})
    
        if insertsp(uploaded_file):
            st.success("Dữ liệu đã được chèn thành công!")
        else:
            st.error("Lỗi khi chèn dữ liệu!")
   
    
    # Custom CSS for text input color
    st.markdown(
        """
        <style>
        /* Change text color and background of all text inputs */
        input[type="text"] {
            color: #1976d2 !important;         /* Text color */
            background-color: #e3f2fd !important; /* Background color */
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Add entry form
    # ...existing code...
    # Add entry form
    st.markdown(
        '<h3 style="color:#ff9800; font-weight:bold;">Scan Barcode and Item Code</h3>',
        unsafe_allow_html=True
    )
    # st.subheader("Scan Barcode and Item Code")
    # ...existing code...
    def trigger_get_data():
        st.session_state['get_data'] = True
    # ...existing code...
    col1, col2, _ = st.columns([0.2, 0.2, 0.6])
    with col1:
        with st.container(border=True):
            item_barcode = st.text_input("Barcode", key="barcode", on_change=trigger_get_data)
    with col2:
        with st.container(border=True):
            item_code = st.text_input("Item Code", key="itemcode", on_change=trigger_get_data)
    st.markdown(
        """
        <style>
        /* Change text color, background, and make input bold */
        input[type="text"] {
            color: #1976d2 !important;
            background-color: #e3f2fd !important;
            font-weight: bold !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    ) 

    # Button for manual trigger
    get_data_clicked = st.button("Get Data")
    # Check if either button was clicked or Enter was pressed
    if get_data_clicked or st.session_state.get('get_data', False):
        data = getsp(st.session_state.get("barcode", ""), st.session_state.get("itemcode", ""))
        st.session_state['get_data'] = False  # Reset flag
        if isinstance(data, str):
            st.error(data)
            return

    if not data.empty:
        st.write("Ket qua:")

        # Extract year and month from BARCODE
        data['Year'] = data['BARCODE'].str[:4]
        data['Month'] = data['BARCODE'].str[4:6]



    # Then group by the higher level, summing Qty and counting rolls
    # First, group by BARCODE to get unique rolls and their Qty
    # Drop duplicates to ensure one Qty per BARCODE
        roll_data = data.drop_duplicates(
            subset=['Store_code', 'Item_desc', 'LOCATOR', 'Year', 'Month', 'BARCODE']
        )

        # Then, group by the higher level, summing Qty and counting rolls
        grouped_data = roll_data.groupby(
            ['Store_code', 'Item_desc', 'LOCATOR', 'Year', 'Month'],
            as_index=False
        ).agg(
            Qty=('Qty', 'sum'),
            Rolls_Count=('BARCODE', 'nunique')
        )

        st.markdown(
            """
            <style>
            .stDataFrame div[data-testid="stVerticalBlock"] {
                font-size: 20px !important;
            }
            .stDataFrame {
                width: 200vw !important;
                min-width: 200vw !important;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
        st.dataframe(grouped_data, use_container_width=True)
        
        return grouped_data
    
if __name__ == "__main__":
    main()