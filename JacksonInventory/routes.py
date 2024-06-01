from JacksonInventory import app
from flask import render_template, redirect, url_for, flash, request, jsonify
from JacksonInventory.models import Item, User, Category, Subcategory
from JacksonInventory.forms import RegisterForm, LoginForm, PurchaseItemForm, SellItemForm, SearchForm
from JacksonInventory import db
from flask_login import login_user, logout_user, login_required, current_user
import requests
from sqlalchemy.sql import text, func

@app.route('/')
@app.route('/home')
def home_page():
    return render_template('home.html')

@app.route('/mainmenu', methods=['GET', 'POST'])
@login_required
def mainmenu_page():
    purchase_form = PurchaseItemForm()
    selling_form = SellItemForm()
    if request.method == "POST":
        # Purchase Item Logic
        purchased_item = request.form.get('purchased_item')
        p_item_object = Item.query.filter_by(name=purchased_item).first()
        if p_item_object:
            if current_user.can_purchase(p_item_object):
                p_item_object.buy(current_user)
                flash(f"Congratulations! You purchased {p_item_object.name} for {p_item_object.price}$", category='success')
            else:
                flash(f"Unfortunately, you don't have enough money to purchase {p_item_object.name}!", category='danger')
        # Sell Item Logic
        sold_item = request.form.get('sold_item')
        s_item_object = Item.query.filter_by(name=sold_item).first()
        if s_item_object:
            if current_user.can_sell(s_item_object):
                s_item_object.sell(current_user)
                flash(f"Congratulations! You sold {s_item_object.name} back to market!", category='success')
            else:
                flash(f"Something went wrong with selling {s_item_object.name}", category='danger')

        return redirect(url_for('mainmenu_page'))

    if request.method == "GET":
        return render_template('mainmenu.html')

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create = User(username=form.username.data, password=form.password1.data)
        db.session.add(user_to_create)
        db.session.commit()
        login_user(user_to_create)
        flash(f"Account created successfully! You are now logged in as {user_to_create.username}", category='success')
        return redirect(url_for('mainmenu_page'))
    if form.errors != {}:
        for err_msg in form.errors.values():
            flash(f'There was an error with creating a user: {err_msg}', category='danger')

    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(attempted_password=form.password.data):
            login_user(attempted_user)
            flash(f'Success! You are logged in as: {attempted_user.username}', category='success')
            return redirect(url_for('mainmenu_page'))
        else:
            flash('Username and password are not match! Please try again', category='danger')

    return render_template('login.html', form=form)

@app.route('/logout')
def logout_page():
    logout_user()
    flash("You have been logged out!", category='info')
    return redirect(url_for("home_page"))

@app.route('/add_item', methods=['GET'])
def add_item_form():
    barcode = request.args.get('barcode')
    category_id = request.args.get('category_id')
    categories = Category.query.order_by(Category.category).all()
    return render_template('add_item.html', barcode=barcode, categories=categories)

@app.route('/add_item', methods=['GET', 'POST'])
def add_item():
    barcode = request.form['barcode']
    productname = request.form['productname']
    qty = request.form['qty']
    minqty = request.form['minqty']
    productimage_input = request.form['productimage']
    category_id = int(request.form['category_id'])
    subcategory_id = int(request.form['subcategory_id'])

    item = Item(barcode=barcode, productname=productname, qty=qty, minqty=minqty, productimage=productimage_input, category_id=category_id, subcategory_id=subcategory_id)

    db.session.add(item)
    db.session.commit()
    flash(f'Product: {productname} has been added with quantity {qty}', category='success')
    return redirect(url_for("add_item_form"))

@app.route('/use_item', methods=['GET'])
# @login_required
def use_item_form():
    barcode = request.args.get('barcode')
    categories = Category.query.order_by(Category.category)
    return render_template('use_item.html', barcode=barcode, categories=categories)

@app.route('/use_item', methods=['POST'])
# @login_required
def use_item():
    barcode = request.form['barcode']
    existing_item = Item.query.filter_by(barcode=barcode).first()

    if existing_item:
        existing_item.qty -= 1  # Decrement the quantity by 1
        db.session.commit()
        product_name = existing_item.productname
        updated_qty = existing_item.qty
        flash(f'Product: {product_name} now has {updated_qty}', category='success')
        return jsonify({
            'product_name': product_name,
            'updated_qty': updated_qty
        })
    else:
        flash(f'Product Not Found', category='danger')
        return jsonify({'barcode_not_found': True})


@app.route('/items')
@login_required
def items_page():
    query = text('''
    SELECT c.id, c.category, COUNT(i.category_id) AS product_count
    FROM category c
    LEFT JOIN item i ON i.category_id = c.id
    GROUP BY c.id, c.category
    ORDER BY c.category
    ''')
    result = db.session.execute(query)
    categories = result.fetchall()

    total_product_count = db.session.query(func.count()).select_from(Item).scalar()

    return render_template('items.html', categories=categories, total_product_count=total_product_count)

@app.route('/category/<int:id>')
@login_required
def category_page(id):
    category = Category.query.get(id)
    query = text('''
    SELECT c.id, i.id as productid, c.category, s.subcategory,
    i.productname, i.qty, i.minqty, i.productimage
    FROM item i
    JOIN category c ON i.category_id = c.id
    JOIN subcategory s ON i.subcategory_id = s.id
    WHERE c.id = :id
    ORDER BY c.category, s.subcategory, i.productname
    ''')
    result = db.session.execute(query, {'id': id}) 
    groceries = result.fetchall()
    return render_template('category.html', category=category, groceries=groceries)

@app.route('/all_categories')
@login_required
def all_categories_page():
    query = text('''
    SELECT c.id, i.id as productid, c.category, s.subcategory,
    i.productname, i.qty, i.minqty, i.productimage
    FROM item i
    JOIN category c ON i.category_id = c.id
    JOIN subcategory s ON i.subcategory_id = s.id
    ORDER BY c.category, s.subcategory, i.productname
    ''')
    result = db.session.execute(query)
    groceries = result.fetchall()
    
    return render_template('category.html', groceries=groceries)

@app.route('/items/<int:id>')
@login_required
def item(id):
    query = text('''
    SELECT c.id as categoryid, i.id as productid, c.category, s.id as subcategoryid, s.subcategory,
    i.productname, i.qty, i.minqty, i.productimage
    FROM item i
    JOIN category c ON i.category_id = c.id
    JOIN subcategory s ON i.subcategory_id = s.id
    WHERE i.id = :id
    ORDER BY c.category, s.subcategory, i.productname
    ''')
    result = db.session.execute(query, {'id': id})
    item = result.fetchall()

    categories_query = Category.query.all()
    subcategories_query = Subcategory.query.all()

    return render_template('item.html', item=item, categories=categories_query, subcategories=subcategories_query)

@app.route('/items/<int:id>', methods=['POST'])
@login_required
def update_item(id):
    updated_productname = request.form.get('productname')
    updated_qty = request.form.get('qty')
    updated_minqty = request.form.get('minqty')
    updated_category_id = request.form.get('category_id')
    updated_subcategory_id = request.form.get('subcategory_id')

    item = Item.query.get(id)
    item.productname = updated_productname
    item.qty = updated_qty
    item.minqty = updated_minqty
    item.category_id = updated_category_id
    item.subcategory_id = updated_subcategory_id

    db.session.commit()

    return redirect(url_for('items_page'))

@app.route('/subcategories', methods=['POST'])
def subcategories():
    category_id = int(request.form['category_id'])
    subcategories = Subcategory.query.filter_by(category_id=category_id).order_by(Subcategory.subcategory).all()
    subcategory_list = [{'id': subcategory.id, 'name': subcategory.subcategory} for subcategory in subcategories]
    return jsonify({'subcategories': subcategory_list})

@app.route('/check_item', methods=['POST'])
@login_required
def check_item():
    barcode = request.form['barcode']
    existing_item = Item.query.filter_by(barcode=barcode).first()

    if existing_item:
        existing_item.qty += 1
        db.session.commit()
        product_name = existing_item.productname
        updated_qty = existing_item.qty
        flash(f'Product: {product_name} now has {updated_qty}', category='success')
        return jsonify({
            'redirect_url': url_for('add_item'),
            'product_name': product_name,
            'updated_qty': updated_qty
        })
    else:
        return jsonify({'barcode_not_found': True})
    
@app.route('/grocery_list', methods=['GET'])
@login_required
def grocery_list():
    query = text('''
    SELECT c.category, i.productname, i.qty, i.minqty
    FROM item i
    JOIN category c ON i.category_id = c.id
    ORDER BY c.category, i.productname
    ''')
    result = db.session.execute(query)
    groceries = result.fetchall()

    grouped_groceries = {}
    for grocery in groceries:
        category = grocery.category
        productname = grocery.productname
        qty = grocery.qty
        minqty = grocery.minqty
        needed_qty = max(0, minqty - qty)
        if needed_qty > 0:
            if category in grouped_groceries:
                grouped_groceries[category].append({
                    'productname': productname,
                    'qty': qty,
                    'minqty': minqty,
                    'needed_qty': needed_qty
                })
            else:
                grouped_groceries[category] = [{
                    'productname': productname,
                    'qty': qty,
                    'minqty': minqty,
                    'needed_qty': needed_qty
                }]

    return render_template('grocery_list.html', grouped_groceries=grouped_groceries)

@app.context_processor
def base():
    form = SearchForm()
    return dict(form=form)

@app.route('/search_start')
@login_required
def search_start():
    return render_template('search_start.html')

@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    form = SearchForm()
    items = Item.query
    if form.validate_on_submit():
        item.searched = form.searched.data
        items = items.filter(Item.productname.like('%' + item.searched + '%'))
        items = items.order_by(Item.barcode).all()
        return render_template("search.html", form=form, searched=item.searched, items=items)
    
def get_product_details(barcode):
    url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
    response = requests.get(url)
    
    if response.status_code == 200:
        product_data = response.json()
        if product_data['status'] == 1:
            product = product_data['product']
            return {
                'name': product.get('product_name', 'N/A'),
                'description': product.get('ingredients_text', 'N/A'),
                'image_url': product.get('image_url', 'N/A')
            }
        else:
            return None
    else:
        return None

@app.route('/srjtest')
def index():
    return render_template('srjtest.html')

@app.route('/mypantry')
def mypantry():
    return render_template('mypantry.html')

@app.route('/product', methods=['POST'])
def product():
    barcode = request.form['barcode']
    product_details = get_product_details(barcode)
    if product_details:
        return jsonify(product_details)
    else:
        return jsonify({'error': 'Product not found or failed to fetch data'}), 404
