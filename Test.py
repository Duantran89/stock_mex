import pandas as pd
import streamlit as st
from conectsupabase import *

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
    print(f"Input: {it}")
    if it != '':

        condition = f' "Item_code" = \'{it}\' '
        print(f"Condition: {condition}")
        df = getdata('stock_mex', "*", condition)

    else:
        columns = "*"
        condition = f' "BARCODE" = \'{inp}\' '
        print(f"Condition: {condition}")
        df_ucc = getdata('stock_mex', columns, condition)
        print(df_ucc)
        it = df_ucc['Item_code'].iloc[0] if not df_ucc.empty else ''

        if not df_ucc.empty:
            columns = "*"
            condition = f' "Item_code" = \'{it}\' '
            print(f"Condition: {condition}")
            df = getdata('stock_mex', columns, condition)

    print(df)
    return df

def main():
    st.title("KIEM TRA KHO MEX")
    data = pd.DataFrame()

    # Add entry form
    st.subheader("Scan Barcode and Item Code")
    
    col1, col2 = st.columns(2)
    with col1:
        item_barcode = st.text_input("Barcode")
    with col2:
        item_code = st.text_input("Item Code")
      

 
    if st.button("Get Data"):
        data = getsp(item_barcode, item_code)
        st.success("Data inserted successfully!")

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
        st.dataframe(grouped_data.iloc[:, 1:], use_container_width=True)
        
        return grouped_data
    
if __name__ == "__main__":
    main()