from fastapi import FastAPI, Response, status
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

# -------------------------
# DATABASE
# -------------------------
products = [
    {"id": 1, "name": "Wireless Mouse", "price": 599, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 99, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "USB Hub", "price": 799, "category": "Electronics", "in_stock": False},
    {"id": 4, "name": "Pen Set", "price": 49, "category": "Stationery", "in_stock": True},
]

# -------------------------
# HOME
# -------------------------
@app.get("/")
def home():
    return {"message": "Store API Running"}

@app.get('/products/audit')
def product_audit():
    in_stock_list = [p for p in products if p['in_stock']]
    out_stock_list = [p for p in products if not p['in_stock']]

    stock_value = sum(p['price'] * 10 for p in in_stock_list)

    priciest = max(products, key=lambda p: p['price'])

    return {
        "total_products": len(products),
        "in_stock_count": len(in_stock_list),
        "out_of_stock_names": [p['name'] for p in out_stock_list],
        "total_stock_value": stock_value,
        "most_expensive": {
            "name": priciest['name'],
            "price": priciest['price']
        }
    }
@app.put("/products/discount")
def apply_discount(category: str, discount_percent: int):
    
    updated_products = []

    for product in products:
        if product["category"].lower() == category.lower():
            new_price = int(product["price"] * (1 - discount_percent / 100))
            product["price"] = new_price
            updated_products.append({
                "name": product["name"],
                "new_price": new_price
            })

    if not updated_products:
        return {"message": f"No products found in category '{category}'"}

    return {
        "updated_count": len(updated_products),
        "products": updated_products
    }
# -------------------------
# GET ALL PRODUCTS
# -------------------------
@app.get("/products")
def get_products():
    return {"products": products, "total": len(products)}

# -------------------------
# PRODUCT MODEL
# -------------------------
class NewProduct(BaseModel):
    name: str
    price: int
    category: str
    in_stock: Optional[bool] = True

# -------------------------
# ADD PRODUCT
# -------------------------
@app.post("/products")
def add_product(data: NewProduct, response: Response):

    for p in products:
        if p["name"].lower() == data.name.lower():
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"error": "Product already exists"}

    next_id = max(p["id"] for p in products) + 1

    new_product = {
        "id": next_id,
        "name": data.name,
        "price": data.price,
        "category": data.category,
        "in_stock": data.in_stock
    }

    products.append(new_product)

    response.status_code = status.HTTP_201_CREATED

    return {"message": "Product added", "product": new_product}

# -------------------------
# UPDATE PRODUCT
# -------------------------
@app.put("/products/{product_id}")
def update_product(product_id: int, price: Optional[int] = None, in_stock: Optional[bool] = None):

    for product in products:
        if product["id"] == product_id:

            if price is not None:
                product["price"] = price

            if in_stock is not None:
                product["in_stock"] = in_stock

            return {"message": "Product updated", "product": product}

    return {"error": "Product not found"}

# -------------------------
# DELETE PRODUCT
# -------------------------
@app.delete("/products/{product_id}")
def delete_product(product_id: int):

    for product in products:
        if product["id"] == product_id:

            products.remove(product)

            return {"message": f"Product '{product['name']}' deleted"}

    return {"error": "Product not found"}