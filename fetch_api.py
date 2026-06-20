import requests   # library to talk to APIs
import json
  
  # 1. Call the API
url = "https://fakestoreapi.com/products"
response = requests.get(url)        # fetch the data

  # 2. Convert JSON text -> Python list
products = response.json()
print(f"✅ Fetched {len(products)} products")
print("First product:", products[0]["title"])
  
  # 3. Save it to a file so we can use it later
with open("data/raw/fakestore_products.json", "w") as f:
  json.dump(products, f, indent=2)
print("✅ Saved to data/raw/fakestore_products.json")