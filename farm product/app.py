from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'supersecretkey'

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products ORDER BY name LIMIT 9').fetchall()
    conn.close()
    return render_template('index.html', products=products)

@app.route('/cart')
def cart():
    cart_items = session.get('cart', [])
    
    # Ensure each item has an image attribute
    for item in cart_items:
        if 'image' not in item:
            item['image'] = 'default-image.jpg'  # Use a default image if none is provided

    cart_total = sum(item['price'] * item['quantity'] for item in cart_items)
    return render_template('cart.html', cart_items=cart_items, cart_total=cart_total)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        account_type = 'regular'

        conn = get_db_connection()
        conn.execute('INSERT INTO users (first_name, last_name, email, username, password, account_type) VALUES (?, ?, ?, ?, ?, ?)',
                     (first_name, last_name, email, username, password, account_type))
        conn.commit()
        conn.close()
        flash('Account created successfully!')
        return redirect(url_for('index'))

    return render_template('register.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/news')
def news():
    return render_template('news.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['account_type'] = user['account_type']
            flash('Login successful!')
            if user['account_type'] == 'superuser':
                return redirect(url_for('stock_management'))
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('index'))

@app.route('/stock_management')
def stock_management():
    if 'user_id' not in session or session.get('account_type') != 'superuser':
        flash('Unauthorized access!')
        return redirect(url_for('login'))

    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products ORDER BY name').fetchall()
    conn.close()
    return render_template('stock_management.html', products=products)

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    conn = get_db_connection()
    product = conn.execute('SELECT * FROM products WHERE id = ?', (id,)).fetchone()

    if request.method == 'POST':
        name = request.form['name']
        type = request.form['type']
        price = request.form['price']
        quantity = request.form['quantity']
        description = request.form['description']
        organic = request.form['organic']

        conn.execute('UPDATE products SET name = ?, type = ?, price = ?, quantity = ?, description = ?, organic = ? WHERE id = ?',
                     (name, type, price, quantity, description, organic, id))
        conn.commit()
        conn.close()
        flash('Product updated successfully!')
        return redirect(url_for('stock_management'))

    conn.close()
    return render_template('edit.html', product=product)

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        name = request.form['name']
        type = request.form['type']
        price = request.form['price']
        quantity = request.form['quantity']
        description = request.form['description']
        organic = request.form['organic']
        date_added = request.form['date_added']

        conn = get_db_connection()
        conn.execute('INSERT INTO products (name, type, price, quantity, description, date_added, organic) VALUES (?, ?, ?, ?, ?, ?, ?)',
                     (name, type, price, quantity, description, date_added, organic))
        conn.commit()
        conn.close()
        flash('Product added successfully!')
        return redirect(url_for('stock_management'))

    return render_template('add.html')

@app.route('/remove/<int:id>', methods=['POST'])
def remove(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM products WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('Product removed successfully!')
    return redirect(url_for('stock_management'))

@app.route('/search')
def search():
    query = request.args.get('query')
    conn = get_db_connection()
    if query:
        products = conn.execute('SELECT * FROM products WHERE name LIKE ?', ('%' + query + '%',)).fetchall()
    else:
        products = conn.execute('SELECT * FROM products ORDER BY name').fetchall()
    conn.close()
    return render_template('search.html', products=products, query=query)

@app.route('/newsletter', methods=['POST'])
def newsletter():
    email = request.form['email']
    conn = get_db_connection()
    conn.execute('INSERT INTO newsletter_emails (email) VALUES (?)', (email,))
    conn.commit()
    conn.close()
    flash('Thank you for signing up for our newsletter!')
    return redirect(url_for('index'))

@app.route('/product/<int:product_id>')
def product_page(product_id):
    conn = get_db_connection()
    product = conn.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
    conn.close()
    if product is None:
        return render_template('404.html')  # Handle product not found error
    return render_template('product_page.html', product=product)

@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    conn = get_db_connection()
    product = conn.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
    if product is None:
        return render_template('404.html')  # Updated to handle product not found error

    cart = session.get('cart', [])
    for item in cart:
        if item['id'] == product_id:
            item['quantity'] += 1
            break
    else:
        cart.append({'id': product_id, 'name': product['name'], 'price': product['price'], 'quantity': 1})
    session['cart'] = cart
    flash(f'Added {product["name"]} to cart.')
    return redirect(url_for('product_page', product_id=product_id))

@app.route('/update_cart', methods=['POST'])
def update_cart():
    cart = session.get('cart', [])
    for item in cart:
        item_id = str(item['id'])
        if item_id in request.form:
            item['quantity'] = int(request.form[item_id])
    session['cart'] = [item for item in cart if item['quantity'] > 0]
    return redirect(url_for('cart'))

@app.route('/remove_from_cart/<int:product_id>')
def remove_from_cart(product_id):
    cart = session.get('cart', [])
    cart = [item for item in cart if item['id'] != product_id]
    session['cart'] = cart
    flash('Item removed from cart.')
    return redirect(url_for('cart'))

@app.route('/checkout')
def checkout():
    # Dummy checkout route, to be implemented later
    return "Checkout page (to be implemented)"



if __name__ == '__main__':
    app.run(debug=True)
