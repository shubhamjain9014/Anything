"""This module provides an example of using SQLite3 for database operations."""
import sqlite3
import re  # import regex
import random
from datetime import datetime
#
from logger_test import logger
# import Flask Package
from flask import Flask, render_template, request, session, redirect, url_for, flash
# connect with Anythin Database
conn = sqlite3.connect("Anything.db")
data_cur = conn.cursor()  # create cursour
with open("script.sql","r") as script:
    myscript = script.read()
    data_cur.executescript(myscript)
# order_data = [
#     (
#         6,
#         6,
#         "2024-05-06",
#         106,
#         "iPhone 7",
#         "Electronics",
#         399.99,
#         1,
#         6,
#         "Emily Davis",
#         "emily@example.com",
#         "777-888-9999",
#         "789 Oak St",
#         "delivered",
#         "2024-05-07",
#     ),
#     (
#         7,
#         7,
#         "2024-05-07",
#         107,
#         "iPhone 7",
#         "Electronics",
#         399.99,
#         1,
#         7,
#         "David Wilson",
#         "david@example.com",
#         "000-111-2222",
#         "890 Cedar St",
#         "pending",
#         "2024-05-09",
#     ),
# ]
# data_cur.executemany(
#     """
#         INSERT INTO orders (
#             orderid, paymentid, order_date, productid, productname, product_category,
#             price, quantity, cusid, cusname, cusemail, cusphone, cus_address,
#             order_status, delivery_date
#         ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
#     """,
#     order_data,
# )
# conn.commit()
# create Customer Table
# create products Table
# insert data in products table
conn.close()
# staring flask
app = Flask(__name__, static_folder="static")
app.secret_key = "jhfejkfeowjfew e iefekfje  fhewoiu fre"  # set the secret key
# starting the base route
@app.route("/", methods=["GET", "POST"])
def home():
    """
    creating Flask Function For Base route
    """
    if "logout" in request.form and request.form["logout"] == "logout":
        session["name"] = None
        flash(message="Logout Successfull", category="warning")
        logger.warning("user logout successfully")
        return render_template("Home/home.html")
    logger.info("Someone Visiting Home page")
    return render_template("Home/home.html")
# This Function is used to check Mail validation
def check_email(s):
    """
    creating mail Function For validation
    """
    pat = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"
    if re.match(pat, s):
        return True
    return False
# Password Validation Registation
def password_check(passwd):
    """
    Check if the password meets the following criteria:
    - At least 6 characters long
    - No more than 20 characters long
    - Contains at least one digit
    - Contains at least one uppercase letter
    - Contains at least one lowercase letter
    - Contains at least one special character ($, @, #, %)
    Parameters:
    passwd (str): The password to check.
    Returns:
    bool: True if the password meets all criteria, False otherwise."""
    spec_char = ["$", "@", "#", "%"]
    val = True
    if len(passwd) < 6:
        val = False
    elif len(passwd) > 20:
        val = False
    elif not any(char.isdigit() for char in passwd):
        val = False
    elif not any(char.isupper() for char in passwd):
        val = False
    elif not any(char.islower() for char in passwd):
        val = False
    elif not any(char in spec_char for char in passwd):
        val = False
    return val
# checking mail is Already exists on Database or Not
def email_existance(email):
    """
    Check if the given email exists in the 'Customer' table.

    Parameters:
    email (str): The email to check.

    Returns:
    bool: True if the email exists, False otherwise.
    """
    connection = sqlite3.connect("Anything.db")
    data_curfun = connection.cursor()
    lst = data_curfun.execute("SELECT email FROM Customer WHERE email=?", (email,))
    exists = lst.fetchone() is not None
    connection.close()
    return exists
def cusid():
    '''Random 7digit customer Id generator'''
    custid = random.randint(1000000, 9999999)
    return custid
# Creating register Route
@app.route("/register", methods=["GET", "POST"])
def register():
    """
    creating Flask register Function For register route
    """
    error = None
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        val_email = check_email(email)
        address = request.form["address"]
        phone = request.form["phone"]
        password = request.form["password"]
        val_pass = password_check(password)
        exis_email = email_existance(email)
        cus_id = cusid()
        if exis_email is False:
            error = "Email Already registered. Please Login using Existing Password."
        if val_email is True & val_pass is True:
            session["email"] = email
            session["password"] = password
            connection = sqlite3.connect("Anything.db")
            cursor = connection.cursor()
            cursor.execute(
                "insert into Customer(id,name,email,phone,address,password)values(?,?,?,?,?,?)",
                (cus_id, name, email, phone, address, password),
            )
            connection.commit()
            connection.close()
            flash(
                message=f"Registered Successfully\nName:{name}\nCustomer Id:{cus_id}",
                category="success",
            )
            logger.info(f"{name},registered to our website")
            return render_template("Auth/login.html")
        error = "Valid Email/Password is not provided Please try again."
        logger.warning("wrong credentials in registration")
    return render_template("Auth/register.html", error=error)
# Creating login Route
@app.route("/login", methods=["GET", "POST"])
def login():
    """
    creating Flask login Function For login route
    """
    error = None
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        connection = sqlite3.connect("Anything.db")
        cursor = connection.cursor()
        data = cursor.execute(
            "select * from Customer where email=? and password=?", (email, password)
        ).fetchone()
        if data:
            if email == data[2] and password == data[5]:
                session["name"] = data[1]
                session["cid"] = data[0]
                name = session["name"]
                flash(message=f"Welcome {name}", category="success")
                logger.info(f"{name} Visiting Home page")
                return redirect(url_for("home"))
            session["name"] = None
            error = "Wroeng Credential Provided . Please Try Again"
            return render_template("Auth/login.html", error=error)
        elif email == "admin@admin.com" and password == "Admin@2024":
            session["name"]="admin"
            flash(message="Admin Login Successfully", category="success")
            logger.info("admin login successfully")
            return redirect(url_for("admin"))
        session["name"] = None
        logger.warning("wrong credentials while login")
        flash(message="Wrong Credentials", category="error")
        return render_template("Auth/login.html", error=error)
    return render_template("Auth/login.html", error=error)
# create profile route
@app.route("/profile", methods=["GET", "POST"])
# using profile function in profile route
def profile():
    connection = sqlite3.connect("Anything.db")
    data_curfun = connection.cursor()
    if session.get("name"):
        cid = session["cid"]
        lst = data_curfun.execute("select * from Customer where id=?", (cid,))
        logger.info(" Visiting Myprofile page")
        return render_template("Profile/myprofile.html", data=lst)
    return render_template("Profile/myprofile.html", data=lst)
# Creating product Route
@app.route("/product", methods=["GET", "POST"])
def product():
    """
    creating Flask products Function For products route
    """
    if request.method == "POST":
        search = request.form.get("search")
        category = request.form.get("category")
        connection = sqlite3.connect("Anything.db")
        data_curfun = connection.cursor()
        if category:
            data_curfun.execute(
                """SELECT * FROM products WHERE product_category LIKE ?""",
                ("%" + category + "%",),
            )
        elif search:
            data_curfun.execute(
                "SELECT * FROM products WHERE product_name LIKE ?",
                ("%" + search + "%",),
            )
        else:
            data_curfun.execute("SELECT * FROM products")
        products = data_curfun.fetchall()
        connection.close()
        return render_template(
            "Products/electronic-products.html", search=search, products=products
        )
    connection = sqlite3.connect("Anything.db")
    data_curfun = connection.cursor()
    data_curfun.execute("SELECT * FROM products")
    products = data_curfun.fetchall()
    connection.close()
    return render_template(
        "Products/electronic-products.html", search=None, products=products
    )
@app.route("/cart", methods=["GET", "POST"])
def view_cart():
    """
    creating Flask view_cart Function For cart route
    """
    connection = sqlite3.connect("Anything.db")
    data_curfun = connection.cursor()
    tp = session.get("total_price", 0)
    if session.get("name"):
        if "btn" in request.form and request.form["btn"] == "plus":
            name = request.form["product_name"]
            var = data_curfun.execute(
                "select * from addtocart where name=?", (name,)
            ).fetchone()
            connection.commit()
            qn = var[2]
            if qn < 10:
                qn += 1
            else:
                qn = 10
            tp = var[3] * qn
            data_curfun.execute(
                "UPDATE addtocart SET quantity=?,tprice=? WHERE name=?;",
                (
                    qn,
                    tp,
                    name,
                ),
            )
            connection.commit()
            lst = data_curfun.execute("select*from addtocart").fetchall()
            total_price = 0
            for i in lst:
                total_price = total_price + i[4]
            return render_template("Cart/cart.html", data=lst, tp=total_price)
        if "btn" in request.form and request.form["btn"] == "minus":
            name = request.form["product_name"]
            var = data_curfun.execute(
                "select * from addtocart where name=?", (name,)
            ).fetchone()
            connection.commit()
            qn = var[2]
            if qn > 2:
                qn -= 1
            else:
                qn = 1
            tp = var[3] * qn
            data_curfun.execute(
                "UPDATE addtocart SET quantity=?,tprice=? WHERE name=?;",
                (
                    qn,
                    tp,
                    name,
                ),
            )
            connection.commit()
            lst = data_curfun.execute("select*from addtocart").fetchall()
            total_price = 0
            for i in lst:
                total_price = total_price + i[4]
            return render_template("Cart/cart.html", data=lst, tp=total_price)
        if "remove" in request.form and request.form["remove"] == "remove":
            cart_id = request.form["cartid"]
            name = request.form["product_name"]
            var = data_curfun.execute(
                "DELETE FROM addtocart WHERE cardid=? and name=?;", (cart_id, name)
            )
            connection.commit()
            lst = data_curfun.execute("select*from addtocart").fetchall()
            total_price = 0
            for i in lst:
                total_price = total_price + i[4]
            return render_template("Cart/cart.html", data=lst, tp=total_price)
        if "btn" in request.form and request.form["btn"] == "back":
            return render_template("Home/home.html")
        if "cart" in request.form and request.form["cart"] == "cart":
            lst = data_curfun.execute("select*from addtocart").fetchall()
            total_price = 0
            for i in lst:
                total_price = total_price + i[4]
            return render_template("Cart/cart.html", data=lst, tp=total_price)
        name = request.form["product_name"]
        price = request.form["price"]
        image = request.form["image_name"]
        var = data_curfun.execute(
            "select name from addtocart where name=?", (name,)
        ).fetchone()
        if var:
            lst = data_curfun.execute("select*from addtocart").fetchall()
            total_price = 0
            for i in lst:
                total_price = total_price + i[4]
            flash(message="Already added", category="warning")
            return render_template("Cart/cart.html", data=lst, tp=total_price)
        quantity = 1
        cid = session["cid"]
        data_curfun.execute(
            "insert into addtocart(cardid,name,quantity,price,tprice,photo)values(?,?,?,?,?,?)",
            (cid, name, quantity, price, price, image),
        )
        connection.commit()
        lst = data_curfun.execute("select*from addtocart").fetchall()
        total_price = 0
        for i in lst:
            total_price = total_price + i[4]
        flash(message="Added to Cart", category="success")
        return render_template("Cart/cart.html", data=lst, tp=total_price)
    error = "Please Login First"
    return render_template("Auth/error.html", error=error)
@app.route("/admin", methods=["GET", "POST"])
def admin():
    """using admin function in "admin" route"""
    connection = sqlite3.connect("Anything.db")
    data_curfun = connection.cursor()
    if "edit" in request.form and request.form["edit"] == "remove":
        connection = sqlite3.connect("Anything.db")
        data_curfun = connection.cursor()
        pid = request.form["pid"]
        data_curfun.execute("DELETE FROM products where product_id=?", (pid,))
        connection.commit()
        show_data = data_curfun.execute("SELECT * FROM products").fetchall()
        flash(message="Product Removed", category="warning")
        logger.warning("Admin removed product")
        return render_template("Admin/admin-view.html", data=show_data, cat="products")
    if request.method == "POST":
        category = request.form.get("category")
        category = category.lower()
        show_data = data_curfun.execute(f"SELECT * FROM {category}").fetchall()
        return render_template("Admin/admin-view.html", data=show_data, cat=category)
    return render_template("Admin/admin.html")
@app.route("/add", methods=["GET", "POST"])
def add():
    """using add function in "add" route"""
    connection = sqlite3.connect("Anything.db")
    data_curfun = connection.cursor()
    if "edit" in request.form and request.form["edit"] == "modify":
        pid = request.form["item"]
        data = data_curfun.execute(
            "select * FROM products where product_id=?", (pid,)
        ).fetchone()
        cat = "edit"
        logger.warning("Admin want to modify product details")
        return render_template("Admin/admin-modify.html", item=data, cat=cat)
    if "edit" in request.form and request.form["edit"] == "add":
        cat = "add"
        logger.warning("Admin want to add product")
        return render_template("Admin/admin-modify.html", cat=cat)
    if "submit" in request.form and request.form["submit"] == "add-btn":
        pid = request.form["p_id"]
        pna = request.form["p_name"]
        pcat = request.form["p_cat"]
        pdesc = request.form["p_desc"]
        ppri = request.form["p_price"]
        ppim = request.form["p_image"]
        ppqn = request.form["p_qn"]
        insert_query = """INSERT INTO products (product_id, product_name, product_category, product_desc, product_price, product_image, product_quan)VALUES (?, ?, ?, ?, ?, ?, ?);"""
        data_curfun.execute(insert_query, (pid, pna, pcat, pdesc, ppri, ppim, ppqn))
        connection.commit()
        category = "products"
        show_data = data_curfun.execute(f"SELECT * FROM {category}").fetchall()
        flash(message="Products Added Successfully", category="success")
        logger.info("Admin succesfully add product")
        return render_template("Admin/admin.html")
    if "submit" in request.form and request.form["submit"] == "modify-btn":
        pid = request.form["p_id"]
        pna = request.form["p_name"]
        pcat = request.form["p_cat"]
        pdesc = request.form["p_desc"]
        ppri = request.form["p_price"]
        ppim = request.form["p_image"]
        ppqn = request.form["p_qn"]
        update_query = """UPDATE products SET product_name=?, product_category=?, product_desc=?, product_price=?, product_image=?, product_quan=?WHERE product_id=?;"""
        data_curfun.execute(update_query, (pna, pcat, pdesc, ppri, ppim, ppqn, pid))
        connection.commit()
        category = "products"
        show_data = data_curfun.execute(f"SELECT * FROM {category}").fetchall()
        flash(message="Product Details Updated", category="success")
        logger.info("Admin succesfully modify product")
        return render_template("Admin/admin-view.html", data=show_data, cat=category)
    if "edit" in request.form and request.form["edit"] == "change-ord":
        order_id = request.form["Order_id"]
        product_id = request.form["pr_id"]
        data = data_curfun.execute(
            "select * FROM orders where orderid=? and productid=? ",
            (order_id, product_id),
        ).fetchone()
        logger.info("Admin want to change order details")
        return render_template("Admin/admin-modify.html", item=data)
    if "submit" in request.form and request.form["submit"] == "edit-add":
        order_id = request.form["Order_id"]
        pr_id = request.form["pr_id"]
        address = request.form["address"]
        o_status = request.form["orderstatus"]
        d_date = request.form["deliverydate"]
        category = "orders"
        data_curfun.execute(
            "UPDATE orders SET cus_address=?, order_status=?, delivery_date=? WHERE orderid=? and productid=? ",
            (address, o_status, d_date, order_id, pr_id),
        )
        connection.commit()
        show_data = data_curfun.execute(f"SELECT * FROM {category}").fetchall()
        logger.info("Admin succesfully changed order details")
        flash(message="Data Updated", category="success")
        return render_template("Admin/admin-view.html", data=show_data, cat=category)
    return render_template("Admin/admin.html")
# validate card details
def cardvalidation(card_number):
    """validate card expiry using python"""
    def validate_credit_card(card_number: str) -> bool:
        card_number = [int(num) for num in card_number]
        check_digit = card_number.pop(-1)
        card_number.reverse()
        card_number = [
            num * 2 if idx % 2 == 0 else num for idx, num in enumerate(card_number)
        ]
        card_number = [
            num - 9 if idx % 2 == 0 and num > 9 else num
            for idx, num in enumerate(card_number)
        ]
        card_number.append(check_digit)
        check_sum = sum(card_number)
        return check_sum % 10 == 0
    return validate_credit_card(card_number)
# validating expiry date
def expiryvalid(exp):
    """validate expiry using python"""

    def valid(exp):
        exp = datetime.strptime(exp, "%m/%Y")
        cdate = datetime.now()
        try:
            if exp > cdate:
                return True
            raise ValueError
        except ValueError:
            return False

    while True:
        try:
            return valid(exp)
        except ValueError:
            return False
# generate order id using python
def generate_order_id():
    """generate order id using python"""
    order_id = "ORD" + "".join(random.choices("0123456789", k=7))
    return order_id
# Genarating paymentid using python
def generate_payment_id():
    """Genarating paymentid using python"""
    order_id = "PYMT" + "".join(random.choices("0123456789", k=5))
    return order_id
@app.route("/payment", methods=["GET", "POST"])
# using payment function in "payment" route
def payment():
    """using payment function in "payment" route"""
    connection = sqlite3.connect("Anything.db")
    data_curfun = connection.cursor()
    cid = session["cid"]
    if request.method == "POST":
        cardno = request.form["cardno"]
        expiry_date = request.form["expiryDate"]
        cvv = request.form["cvv"]
        cardno_val = cardvalidation(cardno)
        cvv_val = True if len(str(cvv)) > 2 else False
        exp_val = expiryvalid(expiry_date)
        if cardno_val is True and cvv_val is True and exp_val is True:
            order_id = generate_order_id()
            payment_id = generate_payment_id()
            cdate = datetime.now()
            pdlist = data_curfun.execute(
                "select * from addtocart where cardid=?", (cid,)
            ).fetchall()
            clist = data_curfun.execute(
                "select name,email,phone,address from Customer where id=?", (cid,)
            ).fetchall()
            for v in clist:
                name = v[0]
                email = v[1]
                phone = v[2]
                address = v[3]
            for p in pdlist:
                pname = p[1]
                pid = data_curfun.execute(
                    "select product_id from products where product_name=?", (pname,)
                ).fetchone()
                pcat = data_curfun.execute(
                    "select product_category from products where product_id=?",
                    (pid[0],),
                ).fetchone()
                img = data_curfun.execute(
                    "select product_image from products where product_id=?",
                    (pid[0],),
                ).fetchone()
                qn = p[2]
                tp = p[4]
                up_data = (
                    order_id,
                    payment_id,
                    cdate,
                    pid[0],
                    pname,
                    pcat[0],
                    tp,
                    qn,
                    cid,
                    name,
                    email,
                    phone,
                    address,
                    "Confirm",
                    cdate,
                    img[0],
                )
                data_curfun.execute(
                    """INSERT INTO orders (orderid, paymentid, order_date, productid, productname, product_category,price, quantity, cusid, cusname, cusemail, cusphone, cus_address,order_status, delivery_date,ordimg) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    up_data,
                )
                connection.commit()
                data_curfun.execute("DELETE FROM addtocart WHERE cardid=?", (cid,))
                connection.commit()
            lst = data_curfun.execute(
                "select * from orders where cusid=?", (cid,)
            ).fetchall()
            total = data_curfun.execute(
                "select sum(tprice) from addtocart where cardid=?", (cid,)
            ).fetchone()
            lstt = data_curfun.execute(
                "select distinct orderid,paymentid from orders where cusid=?", (cid,)
            ).fetchall()
            logger.info(f"{name} successfully pay and placed order")
            flash(message="Order Placed", category="success")
            return render_template(
                "Orders/orders.html", items=lstt, data=lst, total=total
            )
        flash(message="Wrong Credentials", category="error")
        img = data_curfun.execute(
            "select photo from addtocart where cardid=?", (cid,)
        ).fetchall()
        total = data_curfun.execute(
            "select sum(tprice) from addtocart where cardid=?", (cid,)
        ).fetchone()
        return render_template("Payments/payment.html", img=img, total=total)
    img = data_curfun.execute(
        "select photo from addtocart where cardid=?", (cid,)
    ).fetchall()
    total = data_curfun.execute(
        "select sum(tprice) from addtocart where cardid=?", (cid,)
    ).fetchone()
    return render_template("Payments/payment.html", img=img, total=total)
# using paymentsub method route
@app.route("/paymentsub")
def subpay():
    """using subpay function in "paymentsub" route"""
    connection = sqlite3.connect("Anything.db")
    data_curfun = connection.cursor()
    lst = data_curfun.execute("select*from addtocart").fetchall()
    return render_template("Payments/productsinfo.html", data=lst)
@app.route("/orders")
# using orders function in "orders" route
def orders():
    """using order function in "orders" route"""
    connection = sqlite3.connect("Anything.db")
    data_curfun = connection.cursor()
    cid = session["cid"]
    lst = data_curfun.execute(
        "select distinct orderid,paymentid from orders where cusid=?", (cid,)
    ).fetchall()
    items = data_curfun.execute("select * from orders where cusid=?", (cid,)).fetchall()
    logger.info(f"{cid} visiting order details")
    return render_template("Orders/orders.html", items=lst, data=items)
# craeting main Function
if __name__ == "__main__":
    app.run(debug=True)
