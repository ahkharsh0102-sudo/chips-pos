from flask import Flask, render_template, request, redirect, send_file
import sqlite3
import pandas as pd
from datetime import date

app = Flask(__name__)

# -------------------------------
# DATABASE INIT
# -------------------------------

def init_db():
    conn = sqlite3.connect("sales.db")
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS sales(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        item TEXT,
        size TEXT,
        quantity INTEGER,
        price INTEGER,
        total INTEGER
    )
    """)

    conn.commit()
    conn.close()

init_db()

# -------------------------------
# PRICE LOGIC
# -------------------------------

def get_price(item, size):

    menu = {

        "Mexican Loaded Chips":{
            "Small":50,
            "Medium":70,
            "Large":90
        },

        "Tandoori Loaded Chips":{
            "Small":50,
            "Medium":70,
            "Large":90
        },

        "Cheese Volcano":{
            "Small":70,
            "Medium":90,
            "Large":120
        },

        "Fusion Fire":{
            "Small":60,
            "Medium":80,
            "Large":100
        }

    }

    return menu[item][size]


# -------------------------------
# HOME PAGE
# -------------------------------

@app.route("/", methods=["GET","POST"])
def index():

    conn = sqlite3.connect("sales.db")
    cur = conn.cursor()

    if request.method == "POST":

        d = request.form["date"]
        item = request.form["item"]
        size = request.form["size"]
        qty = int(request.form["quantity"])

        price = int(request.form["price"])
        qty = int(request.form["quantity"])

        total = price * qty
        cur.execute(
        "INSERT INTO sales(date,item,size,quantity,price,total) VALUES(?,?,?,?,?,?)",
        (d,item,size,qty,price,total)
        )

        conn.commit()

    # GET SALES DATA
    cur.execute("SELECT * FROM sales")
    data = cur.fetchall()

    # TODAY SALES
    today_str = str(date.today())

    cur.execute("SELECT SUM(total) FROM sales WHERE date=?", (today_str,))
    today_sales = cur.fetchone()[0] or 0

    # TOTAL REVENUE
    cur.execute("SELECT SUM(total) FROM sales")
    revenue = cur.fetchone()[0] or 0

    conn.close()

    return render_template(
        "index.html",
        data=data,
        today=today_sales,
        revenue=revenue,
        today_date=today_str
    )


# -------------------------------
# DELETE RECORD
# -------------------------------

@app.route("/delete/<int:id>")
def delete(id):

    conn = sqlite3.connect("sales.db")
    cur = conn.cursor()

    cur.execute("DELETE FROM sales WHERE id=?", (id,))
    conn.commit()

    # RESET ID ORDER
    cur.execute("CREATE TABLE temp AS SELECT date,item,size,quantity,price,total FROM sales")
    cur.execute("DROP TABLE sales")

    cur.execute("""
    CREATE TABLE sales(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        item TEXT,
        size TEXT,
        quantity INTEGER,
        price INTEGER,
        total INTEGER
    )
    """)

    cur.execute("""
    INSERT INTO sales(date,item,size,quantity,price,total)
    SELECT date,item,size,quantity,price,total FROM temp
    """)

    cur.execute("DROP TABLE temp")

    conn.commit()
    conn.close()

    return redirect("/")


# -------------------------------
# EXPORT EXCEL
# -------------------------------

@app.route("/export")
def export():

    conn = sqlite3.connect("sales.db")

    df = pd.read_sql_query("SELECT * FROM sales", conn)

    file = "sales.xlsx"

    df.to_excel(file, index=False)

    conn.close()

    return send_file(file, as_attachment=True)


# -------------------------------
# RUN APP
# -------------------------------

if __name__ == "__main__":
    app.run(debug=True)