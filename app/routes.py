from flask import render_template, redirect, url_for, request, session, flash
from . import db
from .models import Product, User, CartItem, Order, OrderItem

@app.route('/')
def index():
    products = Product.query.all()
    return render_template('index.html', products=products)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('product.html', product=product)

@app.route('/cart')
def cart():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    cart_items = CartItem.query.filter_by(user_id=user_id).all()
    total = sum([item.product.price * item.quantity for item in cart_items])
    
    return render_template('cart.html', cart_items=cart_items, total=total)

@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    product = Product.query.get_or_404(product_id)

    cart_item = CartItem.query.filter_by(product_id=product.id, user_id=user_id).first()
    if cart_item:
        cart_item.quantity += 1
    else:
        cart_item = CartItem(product_id=product.id, user_id=user_id, quantity=1)
        db.session.add(cart_item)

    db.session.commit()
    flash('Product added to cart!')
    return redirect(url_for('index'))

@app.route('/checkout')
def checkout():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    cart_items = CartItem.query.filter_by(user_id=user_id).all()
    total = sum([item.product.price * item.quantity for item in cart_items])
    
    order = Order(user_id=user_id, total=total)
    db.session.add(order)
    db.session.commit()

    for item in cart_items:
        order_item = OrderItem(order_id=order.id, product_id=item.product.id, quantity=item.quantity)
        db.session.add(order_item)
        db.session.delete(item)
    
    db.session.commit()
    flash('Order placed successfully!')
    return redirect(url_for('order_history'))

@app.route('/order_history')
def order_history():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    orders = Order.query.filter_by(user_id=user_id).all()

    return render_template('order.html', orders=orders)
