from decimal import Decimal

from .models import Product

CART_SESSION_ID = "cart"


class Cart:
    """Session-backed shopping cart: {product_id: quantity}."""

    def __init__(self, request):
        self.session = request.session
        self.cart = self.session.setdefault(CART_SESSION_ID, {})

    def _save(self):
        self.session.modified = True

    def add(self, product, quantity=1, override=False):
        pid = str(product.id)
        current = 0 if override else self.cart.get(pid, 0)
        new_qty = max(0, min(current + quantity, product.stock))
        if new_qty == 0:
            self.cart.pop(pid, None)
        else:
            self.cart[pid] = new_qty
        self._save()

    def remove(self, product):
        self.cart.pop(str(product.id), None)
        self._save()

    def clear(self):
        self.session.pop(CART_SESSION_ID, None)
        self._save()

    def __iter__(self):
        products = Product.objects.filter(id__in=self.cart.keys(), available=True)
        for product in products:
            qty = self.cart[str(product.id)]
            yield {
                "product": product,
                "quantity": qty,
                "line_total": product.price * qty,
            }

    def __len__(self):
        return sum(self.cart.values())

    def total(self):
        return sum((i["line_total"] for i in self), Decimal("0.00"))
