from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

# -------------------------
# PRODUCTS DATABASE
# -------------------------

products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 99, "in_stock": True},
    {"id": 3, "name": "USB Hub", "price": 799, "in_stock": False},
    {"id": 4, "name": "Pen Set", "price": 49, "in_stock": True},
]

# -------------------------
# CART + ORDERS
# -------------------------

cart = []
orders = []

# -------------------------
# ADD TO CART
# -------------------------

@app.post("/cart/add")
def add_to_cart(product_id: int, quantity: int = 1):

    product = next((p for p in products if p["id"] == product_id), None)

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if not product["in_stock"]:
        raise HTTPException(status_code=400, detail=f"{product['name']} is out of stock")

    # check if product already in cart
    for item in cart:
        if item["product_id"] == product_id:
            item["quantity"] += quantity
            item["subtotal"] = item["quantity"] * product["price"]

            return {
                "message": "Cart updated",
                "cart_item": item
            }

    new_item = {
        "product_id": product_id,
        "product_name": product["name"],
        "quantity": quantity,
        "unit_price": product["price"],
        "subtotal": product["price"] * quantity
    }

    cart.append(new_item)

    return {
        "message": "Added to cart",
        "cart_item": new_item
    }


# -------------------------
# VIEW CART
# -------------------------

@app.get("/cart")
def view_cart():

    if not cart:
        return {"message": "Cart is empty"}

    grand_total = sum(item["subtotal"] for item in cart)

    return {
        "items": cart,
        "item_count": len(cart),
        "grand_total": grand_total
    }


# -------------------------
# REMOVE ITEM
# -------------------------

@app.delete("/cart/{product_id}")
def remove_from_cart(product_id: int):

    for item in cart:
        if item["product_id"] == product_id:
            cart.remove(item)
            return {"message": "Item removed from cart"}

    raise HTTPException(status_code=404, detail="Item not in cart")


# -------------------------
# CHECKOUT
# -------------------------

class Checkout(BaseModel):
    customer_name: str
    delivery_address: str


@app.post("/cart/checkout")
def checkout(data: Checkout):

    if not cart:
        raise HTTPException(status_code=400, detail="Cart is empty — add items first")

    order_id = len(orders) + 1

    grand_total = sum(item["subtotal"] for item in cart)

    for item in cart:
        orders.append({
            "order_id": order_id,
            "customer_name": data.customer_name,
            "product": item["product_name"],
            "quantity": item["quantity"],
            "total_price": item["subtotal"]
        })

    cart.clear()

    return {
        "message": "Order placed",
        "grand_total": grand_total
    }


# -------------------------
# VIEW ORDERS
# -------------------------

@app.get("/orders")
def get_orders():
    return {
        "orders": orders,
        "total_orders": len(orders)
    }