import os
import random
from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)
CORS(app)

def get_db_connection():
    return psycopg2.connect(
        host=os.getenv('DB_HOST', 'db'),
        database=os.getenv('DB_NAME', 'shop'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', '123456'),
        cursor_factory=RealDictCursor
    )

@app.route('/api/products', methods=['GET'])
def get_products():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM products;')
    products = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(products)

@app.route('/api/cart', methods=['GET'])
def get_cart():
    session_id = request.args.get('session_id', 'default')
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        SELECT p.id, p.name, p.price, c.quantity 
        FROM cart_items c JOIN products p ON c.product_id = p.id
        WHERE c.session_id = %s
    ''', (session_id,))
    items = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(items)

@app.route('/api/cart', methods=['POST'])
def add_to_cart():
    data = request.json
    session_id = data.get('session_id', 'default')
    product_id = data['product_id']
    quantity = data.get('quantity', 1)
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO cart_items (session_id, product_id, quantity)
        VALUES (%s, %s, %s)
        ON CONFLICT (session_id, product_id) 
        DO UPDATE SET quantity = cart_items.quantity + EXCLUDED.quantity;
    ''', (session_id, product_id, quantity))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({'status': 'added'})

@app.route('/api/cart/<int:product_id>', methods=['DELETE'])
def remove_from_cart(product_id):
    session_id = request.args.get('session_id', 'default')
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM cart_items WHERE session_id = %s AND product_id = %s', (session_id, product_id))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({'status': 'removed'})

@app.route('/api/order', methods=['POST'])
def place_order():
    session_id = request.json.get('session_id', 'default')
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute('''
        SELECT p.id, p.price, c.quantity 
        FROM cart_items c JOIN products p ON c.product_id = p.id
        WHERE c.session_id = %s
    ''', (session_id,))
    cart = cur.fetchall()
    
    if not cart:
        return jsonify({'error': 'Cart is empty'}), 400
        
    total = sum(item['price'] * item['quantity'] for item in cart)
    
    cur.execute('INSERT INTO orders (session_id, total) VALUES (%s, %s) RETURNING id', (session_id, total))
    order_id = cur.fetchone()['id']
    
    for item in cart:
        cur.execute('INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (%s, %s, %s, %s)',
                    (order_id, item['id'], item['quantity'], item['price']))
    
    cur.execute('DELETE FROM cart_items WHERE session_id = %s', (session_id,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({'order_id': order_id, 'total': total})

@app.route('/api/recommend', methods=['GET'])
def recommend():
    session_id = request.args.get('session_id', 'default')
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute('SELECT product_id FROM cart_items WHERE session_id = %s', (session_id,))
    cart_ids = [row['product_id'] for row in cur.fetchall()]
    
    if cart_ids:
        placeholders = ','.join(['%s'] * len(cart_ids))
        cur.execute(f'SELECT * FROM products WHERE id NOT IN ({placeholders}) ORDER BY RANDOM() LIMIT 3', tuple(cart_ids))
    else:
        cur.execute('SELECT * FROM products ORDER BY RANDOM() LIMIT 3')
        
    recs = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(recs)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)