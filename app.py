from flask import Flask, render_template, request, redirect
import json
import os
from datetime import datetime

app = Flask(__name__)

# ==========================================
# JSON DATA FILE
# ==========================================

DATA_FILE = "products.json"
TRANSACTION_FILE = "transactions.json"


def load_products():
    if not os.path.exists(DATA_FILE):
        return []

    with open(DATA_FILE, "r") as file:
        return json.load(file)


def save_products(products):
    with open(DATA_FILE, "w") as file:
        json.dump(products, file, indent=4)


products = load_products()


def load_transactions():
    if not os.path.exists(TRANSACTION_FILE):
        return []

    with open(TRANSACTION_FILE, "r") as file:
        return json.load(file)


def save_transactions(transactions):
    with open(TRANSACTION_FILE, "w") as file:
        json.dump(transactions, file, indent=4)


transactions = load_transactions()

# ==========================================
# DASHBOARD
# ==========================================

@app.route("/")
def home():

    total_products = len(products)

    total_stock = sum(
        product["quantity"]
        for product in products
    )

    low_stock = [
        product
        for product in products
        if 0 < product["quantity"] <= 10
    ]

    out_of_stock = [
        product
        for product in products
        if product["quantity"] == 0
    ]

    inventory_value = sum(
        product["quantity"] * product["price"]
        for product in products
    )

    # Smart Reorder Recommendation

    reorder_products = []

    target_stock = 20

    for product in products:

        if product["quantity"] <= 10:

            reorder_quantity = target_stock - product["quantity"]

            if reorder_quantity < 0:
                reorder_quantity = 0

            reorder_products.append({
                "name": product["name"],
                "quantity": product["quantity"],
                "reorder_quantity": reorder_quantity
            })

    return render_template(
        "index.html",
        products=products,
        total_products=total_products,
        total_stock=total_stock,
        low_stock=low_stock,
        out_of_stock=out_of_stock,
        inventory_value=inventory_value,
        reorder_products=reorder_products
    )


# ==========================================
# ADD PRODUCT
# ==========================================

@app.route("/add", methods=["GET", "POST"])
def add_product():

    if request.method == "POST":

        name = request.form["name"]

        quantity = int(request.form["quantity"])

        price = float(request.form["price"])

        new_id = max(
            [product["id"] for product in products],
            default=0
        ) + 1

        new_product = {
            "id": new_id,
            "name": name,
            "quantity": quantity,
            "price": price
        }

        products.append(new_product)

        # Save permanently
        save_products(products)

        return redirect("/products")

    return render_template("add_product.html")


# ==========================================
# PRODUCTS / SEARCH
# ==========================================

@app.route("/products")
def product_list():

    search = request.args.get(
        "search",
        ""
    ).strip().lower()

    if search:

        filtered_products = [
            product
            for product in products
            if search in product["name"].lower()
        ]

    else:

        filtered_products = products

    return render_template(
        "products.html",
        products=filtered_products,
        search=search
    )


# ==========================================
# STOCK IN
# ==========================================

@app.route(
    "/stock-in/<int:product_id>",
    methods=["POST"]
)
def stock_in(product_id):

    quantity = int(
        request.form["quantity"]
    )

    for product in products:

        if product["id"] == product_id:

            product["quantity"] += quantity

            save_products(products)

            break

    return redirect("/products")


# ==========================================
# STOCK OUT
# ==========================================

@app.route(
    "/stock-out/<int:product_id>",
    methods=["POST"]
)
def stock_out(product_id):

    quantity = int(
        request.form["quantity"]
    )

    for product in products:

        if product["id"] == product_id:

            if quantity <= product["quantity"]:

                product["quantity"] -= quantity

                save_products(products)

            break

    return redirect("/products")


# ==========================================
# DELETE PRODUCT
# ==========================================

@app.route("/delete/<int:product_id>")
def delete_product(product_id):

    global products

    products = [
        product
        for product in products
        if product["id"] != product_id
    ]

    save_products(products)

    return redirect("/products")


# ==========================================
# RUN APPLICATION
# ==========================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )
    