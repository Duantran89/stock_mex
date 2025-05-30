import pandas as pd
from config import SUPABASE_URL, SUPABASE_KEY

from supabase import create_client, Client

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def insertData(table_name: str, data: dict):
    try:
        response = supabase.table(table_name).insert(data).execute()
        if response:
            return True
    except Exception as e:
        return False

def getdata(table_name, columns, condition):
    try:
        response = supabase.rpc('select_data', {
            'table_name': table_name,
            'select_item': columns,
            'conditions': condition
        }).execute()

        if response:
            dt = response.data
            return pd.DataFrame(dt)
    except Exception as e:
        return pd.DataFrame()