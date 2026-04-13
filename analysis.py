from db import get_collection
import pandas as pd
from collections import Counter

def load_data():
    collection = get_collection()
    data = list(collection.find({}, {"_id": 0}))
    return pd.DataFrame(data)

df = load_data()

print("Data loaded from MongoDB")
# print(df.head())

