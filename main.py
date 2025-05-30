import pandas as pd
import streamlit as st
from conectsupabase import *

st.set_page_config(layout="wide")

def insertsp():
    cols = [0, 2, 4, 5, 6, 7]
    data = pd.read_excel(rf"D:\OneDrive - Esquel Group\Warehouse\Data-WH (O)\1. Fabric WH\2. Ket qua Kiem ke hang ngay\Python mex\stock mex.xlsx", usecols=cols, skiprows=1)
    data = data.iloc[:-4]
    data.columns = ['Store_code', 'Item_code', 'Item_desc', 'LOCATOR', 'BARCODE', 'Qty']
    data['Qty'] = data['Qty'].astype(float)
    data['Item_desc'] = data['Item_desc'].str[18:]

    data_json = data.to_dict(orient='records')
    insertData('stock_mex', data_json)

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
    
    # ...existing code...
    col1, col2, _ = st.columns([0.2, 0.2, 0.6])
    with col1:
        with st.container(border=True):
            item_barcode = st.text_input("Barcode")
    with col2:
        with st.container(border=True):
            item_code = st.text_input("Item Code")
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

 
    if st.button("Get Data"):
        data = getsp(item_barcode, item_code)
        if isinstance(data, str):
            st.error(data)
            return
        #st.success("Data inserted successfully!")

    if not data.empty:


        st.write("Ket qua:")
        #st.dataframe(data, use_container_width=True)
        # Add "Rolls" column: count unique BARCODE by Item_code
        data['Rolls'] = data.groupby('Item_code')['BARCODE'].transform('nunique')
        # Extract year and month from BARCODE
        data['Year'] = data['BARCODE'].str[:4]
        data['Month'] = data['BARCODE'].str[4:6]

        grouped_data = data.groupby(['Store_code', 'Item_desc', 'LOCATOR','Year', 'Month'], as_index=False).agg(
            Rolls_Count=("BARCODE", 'nunique')
        ).reset_index()
        # Show the grouped data
        # st.dataframe(grouped_data, use_container_width=True)

        # Show the grouped data without the first two columns
        st.markdown(
            """
            <style>
            /* Make Streamlit dataframe full width and increase font size */
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
        st.dataframe(grouped_data.iloc[:, 1:], use_container_width=True)
        
        return grouped_data
    
if __name__ == "__main__":
    main()