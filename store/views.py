from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Category
from .forms import CheckoutForm
from django.core.paginator import Paginator
from reportlab.pdfgen import canvas
from django.http import HttpResponse
import io

# Home page
def home(request):
    query = request.GET.get('q')
    products_list = Product.objects.all().order_by('-id')
    if query:
        products_list = products_list.filter(name__icontains=query)
    paginator = Paginator(products_list, 8)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)

    # Add int_rating for stars
    for product in products:
        product.stars = [1, 2, 3, 4, 5]
        product.int_rating = int(round(product.rating))


    categories = Category.objects.all()
    return render(request, 'store/index.html', {'products': products, 'categories': categories})


# Category filter
def category_products(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products_list = Product.objects.filter(category=category).order_by('-id')
    paginator = Paginator(products_list, 8)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)

    for product in products:
        product.stars = [1, 2, 3, 4, 5]
        product.int_rating = int(round(product.rating))
    categories = Category.objects.all()
    return render(request, 'store/category.html', {'products': products, 'categories': categories, 'category': category})

# Cart (simple session-based)
def add_to_cart(request, product_id):
    cart = request.session.get('cart', {})
    cart[str(product_id)] = cart.get(str(product_id), 0) + 1
    request.session['cart'] = cart
    return redirect('cart')

def cart(request):
    cart_data = request.session.get('cart', {})
    items = []
    total = 0
    for pid, qty in cart_data.items():
        product = Product.objects.get(id=pid)
        total += product.price_with_gst * qty
        items.append({'product': product, 'qty': qty, 'total': product.price_with_gst*qty})
    return render(request, 'store/cart.html', {'items': items, 'total': total})

# Checkout
# store/views.py

def checkout(request):
    cart_data = request.session.get('cart', {})
    items = []
    total = 0
    for pid, qty in cart_data.items():
        product = Product.objects.get(id=pid)
        total += product.price_with_gst * qty
        items.append({'product': product, 'qty': qty, 'total': float(product.price_with_gst*qty)})

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Save form data in session for later use
            request.session['checkout_data'] = form.cleaned_data
            request.session['cart_total'] = float(total)  # <-- convert to float
            return redirect('phonepe_payment')
    else:
        form = CheckoutForm()
    return render(request, 'store/checkout.html', {'form': form, 'items': items, 'total': total})



# Dummy Payment
def payment(request):
    if request.method == 'POST':
        return redirect('invoice_pdf')
    return render(request, 'store/payment.html')

# Generate PDF invoice
def invoice_pdf(request):
    checkout_data = request.session.get('checkout_data', {})
    cart_data = request.session.get('cart', {})

    if not checkout_data or not cart_data:
        return redirect('home')

    # Generate PDF invoice
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, 800, "Vetri shopify E-Commerce Invoice")
    p.setFont("Helvetica", 12)
    p.drawString(50, 780, f"Customer: {checkout_data.get('name')}")
    p.drawString(50, 760, f"Email: {checkout_data.get('email')}")
    p.drawString(50, 740, f"Phone: {checkout_data.get('phone')}")
    p.drawString(50, 720, f"Address: {checkout_data.get('address')}")

    y = 680
    total = 0
    for pid, qty in cart_data.items():
        product = Product.objects.get(id=pid)
        line_total = product.price_with_gst * qty
        p.drawString(50, y, f"{product.name} x {qty} - ₹{line_total}")
        total += line_total
        y -= 20

    p.drawString(50, y-10, f"Grand Total: ₹{total}")
    p.showPage()
    p.save()
    buffer.seek(0)

    # Clear cart/session after payment
    request.session['cart'] = {}
    request.session['cart_total'] = 0
    request.session['checkout_data'] = {}

    return HttpResponse(buffer, content_type='application/pdf')



def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    product_id = str(product_id)
    if product_id in cart:
        del cart[product_id]
        request.session['cart'] = cart
    return redirect('cart')

def update_cart(request, product_id):
    if request.method == "POST":
        cart = request.session.get("cart", {})
        action = request.POST.get("action")
        current_qty = cart.get(str(product_id), 1)

        if action == "increase":
            cart[str(product_id)] = current_qty + 1
        elif action == "decrease":
            if current_qty > 1:
                cart[str(product_id)] = current_qty - 1
            else:
                cart.pop(str(product_id), None)
        else:  # fallback if qty input is used
            try:
                qty = int(request.POST.get("qty", 1))
                if qty > 0:
                    cart[str(product_id)] = qty
                else:
                    cart.pop(str(product_id), None)
            except ValueError:
                pass  # ignore invalid input

        request.session['cart'] = cart
    return redirect('cart')

import uuid

def phonepe_payment(request):
    checkout_data = request.session.get('checkout_data', {})
    amount = request.session.get('cart_total', 0)
    order_id = str(uuid.uuid4())  # Generate dummy order ID

    if not checkout_data:
        return redirect('checkout')

    return render(request, 'store/phonepe_payment.html', {'order_id': order_id, 'amount': amount})
