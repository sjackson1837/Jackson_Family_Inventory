from JacksonInventory import app
from flask import render_template, redirect, url_for, flash, request, jsonify
from JacksonInventory.models import Item, User, Category, Subcategory
from JacksonInventory.forms import RegisterForm, LoginForm, SearchForm
from JacksonInventory import db
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy.sql import text, func
from sqlalchemy.exc import IntegrityError
import requests

@app.route('/')
@app.route('/home')
def home_page():
    return render_template('home.html')

@app.route('/mainmenu', methods=['GET'])
@login_required
def mainmenu_page():
    selected_category = request.args.get('category')
    selected_subcategory = request.args.get('subcategory')
    search_query = request.args.get('search')

    # Trim the search query to remove leading and trailing spaces
    search_query = search_query.strip() if search_query else None

    # Query to fetch all distinct categories for the sidebar
    category_query = text('''
    SELECT DISTINCT c.id, c.category
    FROM category c
    JOIN item i ON i.category_id = c.id
    ORDER BY c.category
    ''')
    categories_result = db.session.execute(category_query)
    categories = categories_result.fetchall()

    # Initialize subcategories
    subcategories = []

    # Convert search_query to lower case for case-insensitive comparison
    search_query_lower = search_query.lower() if search_query else None

    if search_query_lower and search_query_lower.strip():  # Check if search_query is not empty or just whitespace
        # Query to fetch items based on the search query (case-insensitive)
        item_query = text('''
        SELECT c.category, s.subcategory, i.productimage, i.qty, i.minqty, i.productname, i.id as productid
        FROM item i
        JOIN category c ON i.category_id = c.id
        JOIN subcategory s ON i.subcategory_id = s.id
        WHERE LOWER(i.productname) LIKE :search_query
        OR LOWER(i.barcode) LIKE :search_query
        ORDER BY c.category, i.productname
        ''')
        items_result = db.session.execute(item_query, {
            'search_query': f"%{search_query_lower}%"
        })
    else:
        # No search query or just whitespace, so show all items
        if selected_category:
            # Query to fetch subcategories based on the selected category
            subcategory_query = text('''
            SELECT DISTINCT s.id, s.subcategory
            FROM subcategory s
            JOIN item i ON i.subcategory_id = s.id
            JOIN category c ON i.category_id = c.id
            WHERE c.category = :category
            ORDER BY s.subcategory
            ''')
            subcategories_result = db.session.execute(subcategory_query, {'category': selected_category})
            subcategories = subcategories_result.fetchall()

            # Query to fetch items based on the selected category, subcategory, and optional search query (case-insensitive)
            item_query = text('''
            SELECT c.category, s.subcategory, i.productimage, i.qty, i.minqty, i.productname, i.id as productid
            FROM item i
            JOIN category c ON i.category_id = c.id
            JOIN subcategory s ON i.subcategory_id = s.id
            WHERE c.category = :category
            AND (s.subcategory = :subcategory OR :subcategory IS NULL)
            AND (LOWER(i.productname) LIKE :search_query OR LOWER(i.barcode) LIKE :search_query OR :search_query IS NULL)
            ORDER BY i.productname
            ''')
            items_result = db.session.execute(item_query, {
                'category': selected_category,
                'subcategory': selected_subcategory,
                'search_query': f"%{search_query_lower}%" if search_query_lower else None
            })
        else:
            # If no category is selected, show all items (case-insensitive)
            item_query = text('''
            SELECT c.category, s.subcategory, i.productimage, i.qty, i.minqty, i.productname, i.id as productid
            FROM item i
            JOIN category c ON i.category_id = c.id
            JOIN subcategory s ON i.subcategory_id = s.id
            WHERE LOWER(i.productname) LIKE :search_query OR LOWER(i.barcode) LIKE :search_query OR :search_query IS NULL
            ORDER BY c.category, i.productname
            ''')
            items_result = db.session.execute(item_query, {
                'search_query': f"%{search_query_lower}%" if search_query_lower else None
            })

    items = items_result.fetchall()

    return render_template('mainmenu.html', categories=categories, subcategories=subcategories, items=items, selected_category=selected_category, selected_subcategory=selected_subcategory)


@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        print("Am I here????")
        if form.password1.data == form.password2.data:
            print("Am I here????2222222")
            user_to_create = User(username=form.username.data,
                                  password=form.password1.data)
            db.session.add(user_to_create)
            db.session.commit()
            login_user(user_to_create)
            flash(f"Account created successfully! You are now logged in as {user_to_create.username}", category='success')
            return redirect(url_for('mainmenu_page'))
        else:
            flash('Passwords must match!', category='danger')
    if form.errors != {}:
        for err_msg in form.errors.values():
            flash(f'There was an error with creating a user: {err_msg}', category='danger')

    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        print(attempted_user)
        if attempted_user and attempted_user.check_password_correction(
                attempted_password=form.password.data
        ):
            login_user(attempted_user)
            flash(f'Success! You are logged in as: {attempted_user.username}', category='success')
            print(attempted_user)
            return redirect(url_for('mainmenu_page'))
        else:
            flash('Username and password are not match! Please try again', category='danger')

    return render_template('login.html', form=form)

@app.route('/logout')
def logout_page():
    logout_user()
    flash("You have been logged out!", category='info')
    return redirect(url_for("home_page"))




# @app.route('/items')
# @login_required
# def items_page():
#     query = text('''
#     SELECT c.id, c.category, COUNT(i.category_id) AS product_count
#     FROM category c
#     LEFT JOIN item i ON i.category_id = c.id
#     GROUP BY c.id, c.category
#     ORDER BY c.category
#     ''')
#     result = db.session.execute(query)
#     categories = result.fetchall()

#     # Retrieve the total product count
#     total_product_count = db.session.query(func.count()).select_from(Item).scalar()

#     return render_template('items.html', categories=categories, total_product_count=total_product_count)

@app.route('/category/<int:id>')
@login_required
def category_page(id):
    # Retrieve products for the specified category
    category = Category.query.get(id)
    query = text('''
    SELECT c.id, i.id as productid, c.category, s.subcategory,
    i.productname, i.qty, i.minqty, i.productimage
    FROM item i
    JOIN category c ON i.category_id = c.id
    JOIN subcategory s ON i.subcategory_id = s.id
    WHERE c.id = :id  -- Filter by the category ID
    ORDER BY c.category, s.subcategory,     i.productname
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
    result = db.session.execute(query, {'id': id})  # Pass the 'id' value as a parameter
    item = result.fetchall()

    # Retrieve categories and subcategories from the database
    categories_query = Category.query.all()
    subcategories_query = Subcategory.query.all()

    # Pass categories and subcategories to the template
    return render_template('item.html', item=item, categories=categories_query, subcategories=subcategories_query)


@app.route('/items/<int:id>', methods=['POST'])
@login_required
def update_item(id):
    # Retrieve the updated values from the form
    updated_productname = request.form.get('productname')
    print(updated_productname)
    updated_qty = request.form.get('qty')
    updated_minqty = request.form.get('minqty')
    updated_category_id = request.form.get('category_id')
    print(updated_category_id)
    updated_subcategory_id = request.form.get('subcategory_id')
    print(updated_subcategory_id)
    updated_image_url = request.form.get('productimage')
    print(updated_image_url)

    # Update the item in the database
    item = Item.query.get(id)
    item.productname = updated_productname
    item.qty = updated_qty
    item.minqty = updated_minqty
    item.category_id = updated_category_id
    print(updated_category_id)
    item.subcategory_id = updated_subcategory_id
    item.productimage = updated_image_url

    db.session.commit()

    # Redirect to the item view page or any other appropriate response
    return redirect(url_for('mainmenu_page'))

@app.route('/add_item', methods=['GET'])
def add_item_form():
    barcode = request.args.get('barcode', '')
    categories = Category.query.order_by(Category.category).all()
    return render_template('add_item.html', barcode=barcode, categories=categories)


@app.route('/add_item', methods=['POST'])
def add_item():
    barcode = request.form.get('barcode')
    productname = request.form.get('productname')
    qty = request.form.get('qty')
    minqty = request.form.get('minqty')
    productimage_input = request.form.get('productimage')
    category_id = int(request.form.get('category_id', 0))  # Default to 0 if not provided
    subcategory_id = int(request.form.get('subcategory_id', 0))  # Default to 0 if not provided

    # Validate required fields
    if not barcode or not productname or not qty or not minqty or not category_id:
        return jsonify({'error': 'All required fields must be filled out'}), 400

    # Create a new Item object and set its attributes
    item = Item(barcode=barcode, productname=productname, qty=qty, minqty=minqty, productimage=productimage_input, category_id=category_id, subcategory_id=subcategory_id)

    # Save the item to the database
    db.session.add(item)
    db.session.commit()

    # Return a success response or redirect to another page
    return redirect(url_for("add_item_form", barcode=barcode))

# Add the following route to handle the AJAX request for subcategories
@app.route('/subcategories', methods=['POST'])
def subcategories():
    # Retrieve the selected category ID from the AJAX request
    category_id = int(request.form['category_id'])

    # Query the subcategories based on the selected category ID
    subcategories = Subcategory.query.filter_by(category_id=category_id).order_by(Subcategory.subcategory).all()

    # Create a list of dictionaries containing subcategory details
    subcategory_list = [{'id': subcategory.id, 'name': subcategory.subcategory} for subcategory in subcategories]

    # Return the subcategories as JSON response
    return jsonify({'subcategories': subcategory_list})


@app.route('/fetch_product_info/<barcode>', methods=['GET'])
def fetch_product_info(barcode):
    url = f'https://api.upcitemdb.com/prod/trial/lookup?upc={barcode}'
    print(url)
    response = requests.get(url)
    
    # Extract rate limit headers
    rate_limit_limit = response.headers.get('X-RateLimit-Limit')
    rate_limit_remaining = response.headers.get('X-RateLimit-Remaining')
    rate_limit_reset = response.headers.get('X-RateLimit-Reset')

    rate_limit_info = {
        'rate_limit_limit': rate_limit_limit,
        'rate_limit_remaining': rate_limit_remaining,
        'rate_limit_reset': rate_limit_reset
    }

    if response.status_code == 200:
        data = response.json()
        if 'items' in data and len(data['items']) > 0:
            item = data['items'][0]
            title = item.get('title', '')
            images = item.get('images', [])
            image = images[0] if images else ''
            print(rate_limit_info)
            return jsonify({'found': True, 'title': title, 'image': image, **rate_limit_info})
        else:
            return jsonify({'found': False, **rate_limit_info})
    else:
        try:
            error_data = response.json()
            error_code = error_data.get('code', 'UNKNOWN_ERROR')
            error_message = error_data.get('message', 'Unknown error occurred.')
        except ValueError:
            error_code = 'UNKNOWN_ERROR'
            error_message = 'Unknown error occurred.'

        return jsonify({'found': False, 'error_code': error_code, 'error_message': error_message, **rate_limit_info}), response.status_code


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
        # Redirect to the /use_item webpage
        return redirect(url_for('use_item'))
    else:
        # flash(f'Barcode Not Found')
        # flash(f'Barcode Not Found', category='success')
        return redirect(url_for('use_item'))
    

#Pass Stuff to Navbar
@app.context_processor
def base():
    form = SearchForm()
    return dict(form=form)

# @app.route('/search_start')
# @login_required
# def search_start():
#     return render_template('search_start.html')

# @app.route('/search', methods=['GET', 'POST'])
# @login_required
# def search():
#     form = SearchForm()
#     items = Item.query
#     if form.validate_on_submit():
#         # Get data from submitted form
#         searched = form.searched.data.lower()  # Convert to lowercase
        
#         # Query the Database, convert column values to lowercase for case-insensitive search
#         items = items.filter(func.lower(Item.productname).like('%' + searched + '%'))
#         items = items.order_by(Item.barcode).all()
#         return render_template("search.html", form=form, searched=searched, items=items)
    

# @app.route('/srjtest')
# @login_required
# def srjtest():
#     return render_template('srjtest.html')

@app.route('/lookup', methods=['GET'])
def lookup():
    upc = request.args.get('upc')
    url = f"https://api.upcitemdb.com/prod/trial/lookup?upc={upc}"
    #headers = {'user_key': API_KEY}
    # response = requests.get(url, headers=headers)
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if 'items' in data and data['items']:
            item = data['items'][0]
            result = {
                'title': item.get('title', 'N/A'),
                'image': item.get('images', [''])[0],
                'price': item.get('lowest_recorded_price', 'N/A')
            }
            return jsonify(result)
    return render_template('lookup.html')

@app.route('/save', methods=['POST'])
def save():
    data = request.form
    item = {
        'barcode': data.get('barcode'),
        'productname': data.get('productname'),
        'qty': data.get('qty'),
        'minqty': data.get('minqty'),
        'productimage': data.get('productimage'),
        'category_id': data.get('category_id'),
        'subcategory_id': data.get('subcategory_id')
    }
    # Here you would save the item to the database
    # For now, just print it to the console
    print(item)
    return redirect(url_for('index'))

@app.route('/save_new_item', methods=['POST'])
@login_required
def save_new_item():
    data = request.json
    print(data)  # Debug: Print the received data
    barcode = data.get('barcode')
    productname = data.get('productname')
    qty = data.get('qty', 1)
    minqty = data.get('minqty', 1)
    category_id = data.get('category_id')
    subcategory_id = data.get('subcategory_id')
    productimage = data.get('productimage')

    print(f"Creating new item: {barcode}, {productname}, {qty}, {minqty}, {category_id}, {subcategory_id}, {productimage}")  # Debug

    # Create a new item
    try:
        new_item = Item(
            barcode=barcode,
            productname=productname,
            qty=qty,
            minqty=minqty,
            category_id=category_id,
            subcategory_id=subcategory_id,
            productimage=productimage
        )

        db.session.add(new_item)
        db.session.commit()
        print("New item committed to the database")  # Debug
    except IntegrityError as e:
        print(f"Integrity error: {e}")  # Debug
        db.session.rollback()
        return jsonify({'error': 'There was an error saving the new item.'}), 500

    return jsonify({'message': 'New item saved successfully!'}), 201

@app.route('/check_barcode/<barcode>', methods=['GET'])
@login_required
def check_barcode(barcode):
    item = Item.query.filter_by(barcode=barcode).first()
    if item:
        return jsonify({'found': True})
    else:
        return jsonify({'found': False})


@app.route('/updateitem/<string:barcode>', methods=['POST'])
def updateitem(barcode):
    try:
        data = request.get_json()
        productname = data['productname']
        qty = data['qty']
        minqty = data['minqty']
        category = data['category']
        subcategory = data['subcategory']
        productimage = data['productimage']

        # Update the item in the database
        item = Item.query.filter_by(barcode=barcode).first()
        if item:
            item.productname = productname
            item.qty = qty
            item.minqty = minqty
            item.category_id = category
            item.subcategory_id = subcategory
            item.productimage = productimage

            db.session.commit()
            return jsonify({'message': 'Item updated successfully!'})
        else:
            return jsonify({'error': 'Item not found'}), 404
    except KeyError as e:
        return jsonify({"error": f"Missing field: {e}"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/get_categories', methods=['GET'])
@login_required
def get_categories():
    categories = Category.query.order_by(Category.category).all()  # Sort categories alphabetically
    subcategories = Subcategory.query.order_by(Subcategory.subcategory).all()  # Sort subcategories alphabetically

    categories_list = [{'id': c.id, 'category': c.category} for c in categories]
    subcategories_list = [{'id': s.id, 'subcategory': s.subcategory, 'category_id': s.category_id} for s in subcategories]

    return jsonify({'categories': categories_list, 'subcategories': subcategories_list})

@app.route('/get_categories/<int:category_id>', methods=['GET'])
@login_required
def get_subcategories(category_id):
    # Query subcategories associated with the given category ID and sort alphabetically
    subcategories = Subcategory.query.filter_by(category_id=category_id).order_by(Subcategory.subcategory).all()

    # Create a list of dictionaries containing subcategory details
    subcategories_list = [{'id': s.id, 'subcategory': s.subcategory} for s in subcategories]

    return jsonify({'subcategories': subcategories_list})


@app.route('/increment_qty/<barcode>', methods=['POST'])
def increment_qty(barcode):
    item = Item.query.filter_by(barcode=barcode).first()
    if item:
        item.qty += 1
        db.session.commit()
        return jsonify({'message': 'Item quantity increased by 1'})
    else:
        return jsonify({'error': 'Item not found'}), 404




@app.route('/decrement_qty/<barcode>', methods=['POST'])
def decrement_qty(barcode):
    item = Item.query.filter_by(barcode=barcode).first()
    if item:
        item.qty -= 1
        db.session.commit()
        return jsonify({'message': f'{item.productname} has been decreased by 1. New quantity: {item.qty}'})
    else:
        return jsonify({'error': 'Item not found'}), 404


@app.route('/additem', methods=['POST'])
def additem():
    try:
        data = request.get_json()
        barcode = data['barcode']
        productname = data['productname']
        qty = data['qty']
        minqty = data['minqty']
        category = data['category']
        subcategory = data['subcategory']
        productimage = data['productimage']
        
        # Check if the item already exists in the database
        existing_item = Item.query.filter_by(barcode=barcode).first()
        if existing_item:
            return jsonify({"error": "Item already exists in the database"}), 400

        # Create a new item object
        new_item = Item(
            barcode=barcode,
            productname=productname,
            qty=qty,
            minqty=minqty,
            category_id=category,
            subcategory_id=subcategory,
            productimage=productimage
        )

        # Add the new item to the database
        db.session.add(new_item)
        db.session.commit()

        return jsonify({"message": "Item added successfully!"}), 201
    except KeyError as e:
        return jsonify({"error": f"Missing field: {e}"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route('/base_new')
@login_required
def base_new():
    return render_template('base_new.html')

@app.route('/useitem')
def useitem():
    return render_template('use_item.html')


if __name__ == '__main__':
    app.run(debug=True)