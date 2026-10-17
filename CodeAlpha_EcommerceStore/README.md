# CodeAlpha_EcommerceStore

**Task 1 – Simple E-commerce Store** for the CodeAlpha Full Stack Development internship.

A Django (Python) store with an HTML/CSS/JavaScript frontend and a SQLite database.

## Features

- Category menu bar at the top of every page: hover a category (tap on mobile) to open its subcategories
- Product listings with categories and subcategories, search, sorting and pagination (opening a parent category also shows its subcategories' products)
- Product details page with stock status and related products
- Shopping cart (session based) with add / update quantity / remove, and AJAX "Add to cart" with a toast and live cart badge
- User registration, login and logout (unique email enforced)
- Checkout and order processing: stock is validated and decremented inside a database transaction; prices are frozen on each order item
- Order history per user; users can only see their own orders
- Django admin to manage categories, products, orders (with inline order items) and order status
- 9 automated tests covering the main flows

## Database models

`Category` (optional `parent` for subcategories) → `Product` → `OrderItem` ← `Order` ← `User`

To add a subcategory, go to Admin → Categories → Add, and pick a parent. Products are normally assigned to a subcategory.

If you already ran an earlier version, just run `python manage.py migrate` and then `python manage.py seed` again; existing sample products are moved into the new subcategories.

## Run it locally

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python manage.py migrate
python manage.py seed             # sample categories and products
python manage.py createsuperuser  # optional, for /admin/
python manage.py runserver
```

Open http://127.0.0.1:8000/

## Run the tests

```bash
python manage.py test store
```

## Project structure

```
config/                 Django project settings and root URLs
store/
  models.py             Category, Product, Order, OrderItem
  cart.py               Session-backed Cart class
  views.py              Listing, detail, cart, auth, checkout, orders
  forms.py              Registration and checkout forms
  templates/            HTML templates (store/ and registration/)
  static/store/         style.css and app.js
  management/commands/  seed.py (sample data)
  tests.py              Automated tests
```

## Notes

- Payment is simulated; orders are saved with status "Pending".
- Product images in the seed data use placeholder URLs from picsum.photos, so they need internet access to show. You can also upload images in the admin.
- `DEBUG` and `SECRET_KEY` in `config/settings.py` are for development only.
