from JacksonInventory import app
from flask import render_template, redirect, url_for, flash, request, jsonify
from JacksonInventory.models import Item, User, Category
from JacksonInventory.forms import RegisterForm, LoginForm, PurchaseItemForm, SellItemForm
from JacksonInventory import db
from flask_login import login_user, logout_user, login_required, current_user
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
        #Purchase Item Logic
        purchased_item = request.form.get('purchased_item')
        p_item_object = Item.query.filter_by(name=purchased_item).first()
        if p_item_object:
            if current_user.can_purchase(p_item_object):
                p_item_object.buy(current_user)
                flash(f"Congratulations! You purchased {p_item_object.name} for {p_item_object.price}$", category='success')
            else:
                flash(f"Unfortunately, you don't have enough money to purchase {p_item_object.name}!", category='danger')
        #Sell Item Logic
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
        # items = Item.query.filter_by(owner=None)
        # owned_items = Item.query.filter_by(owner=current_user.id)
        return render_template('mainmenu.html')

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create = User(username=form.username.data,
                              password=form.password1.data)
        db.session.add(user_to_create)
        db.session.commit()
        login_user(user_to_create)
        flash(f"Account created successfully! You are now logged in as {user_to_create.username}", category='success')
        return redirect(url_for('mainmenu_page'))
    if form.errors != {}: #If there are not errors from the validations
        for err_msg in form.errors.values():
            flash(f'There was an error with creating a user: {err_msg}', category='danger')

    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(
                attempted_password=form.password.data
        ):
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



from sqlalchemy import func

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

    # Retrieve the total product count
    total_product_count = db.session.query(func.count()).select_from(Item).scalar()

    return render_template('items.html', categories=categories, total_product_count=total_product_count)

@app.route('/category/<int:id>')
@login_required
def category_page(id):
    # Retrieve products for the specified category
    category = Category.query.get(id)
    print(id)
    query = text('''
    SELECT c.id, i.id as productid, c.category, i.productname, i.qty, i.minqty, i.productimage
    FROM item i
    JOIN category c ON i.category_id = c.id
    WHERE c.id = :id  -- Filter by the category ID
    ORDER BY c.category, i.productname
    ''')
    result = db.session.execute(query, {'id': id}) 
    groceries = result.fetchall()
    return render_template('category.html', category=category, groceries=groceries)

@app.route('/all_categories')
@login_required
def all_categories_page():
    query = text('''
    SELECT c.id, i.id as productid, c.category, i.productname, i.qty, i.minqty, i.productimage
    FROM item i
    JOIN category c ON i.category_id = c.id
    ORDER BY c.category, i.productname
    ''')
    result = db.session.execute(query)
    groceries = result.fetchall()
    
    return render_template('category.html', groceries=groceries)

@app.route('/items/<int:id>')
@login_required
def item(id):
    item = Item.query.get_or_404(id)
    return render_template('item.html', item=item)

@app.route('/add_item', methods=['GET'])
@login_required
def add_item_form():
    barcode = request.args.get('barcode')
    categories = Category.query.order_by(Category.category)
    return render_template('add_item.html', barcode=barcode, categories=categories)

@app.route('/add_item', methods=['POST'])
@login_required
def add_item():
    barcode = request.form['barcode']
    productname = request.form['productname']
    qty = request.form['qty']
    minqty = request.form['minqty']
    productimage = request.form['productimage']
    category_id = request.form['category_id']

    # Create a new Item object and set its attributes
    item = Item(barcode=barcode, productname=productname, qty=qty, minqty=minqty, productimage=productimage, category_id=category_id)

    # Save the item to the database
    db.session.add(item)
    db.session.commit()
    #return redirect(url_for("items_page"))
    return redirect(url_for("add_item"))

@app.route('/check_item', methods=['POST'])
@login_required
def check_item():
    barcode = request.form['barcode']
    existing_item = Item.query.filter_by(barcode=barcode).first()

    if existing_item:
        existing_item.qty += 1  # Increment the quantity by 1
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
        needed_qty = max(0, minqty - qty)  # Calculate needed qty
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

@app.route('/use_item', methods=['GET'])
@login_required
def use_item_form():
    barcode = request.args.get('barcode')
    categories = Category.query.order_by(Category.category)
    return render_template('use_item.html', barcode=barcode, categories=categories)

@app.route('/use_item', methods=['POST'])
@login_required
def use_item():
    barcode = request.form['barcode']
    existing_item = Item.query.filter_by(barcode=barcode).first()

    if existing_item:
        existing_item.qty -= 1  # Increment the quantity by 1
        db.session.commit()
        product_name = existing_item.productname
        updated_qty = existing_item.qty
        flash(f'Product: {product_name} now has {updated_qty}', category='success')
        return jsonify({
            'redirect_url': url_for('use_item'),
            'product_name': product_name,
            'updated_qty': updated_qty
        })
    else:
        return jsonify({'barcode_not_found': True})