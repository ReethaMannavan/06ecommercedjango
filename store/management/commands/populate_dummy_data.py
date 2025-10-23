from django.core.management.base import BaseCommand
from store.models import Category, Product
from django.utils.text import slugify
import random
import os
from django.core.files import File

class Command(BaseCommand):
    help = 'Populate dummy categories and products'

    def handle(self, *args, **kwargs):
        categories = ['Electronics', 'Fashion', 'Books', 'Home Appliances']
        product_names = {
            'Electronics': ['Smartphone', 'Laptop', 'Headphones', 'Smartwatch', 'Camera'],
            'Fashion': ['T-Shirt', 'Jeans', 'Sneakers', 'Jacket', 'Sunglasses'],
            'Books': ['Python Programming', 'Data Analysis', 'Machine Learning', 'Django for Beginners', 'Java Fundamentals'],
            'Home Appliances': ['Microwave', 'Blender', 'Vacuum Cleaner', 'Air Purifier', 'Coffee Maker']
        }

        # Create categories
        for cat_name in categories:
            cat, created = Category.objects.get_or_create(name=cat_name, slug=slugify(cat_name))
            if created:
                self.stdout.write(self.style.SUCCESS(f'Category "{cat_name}" created.'))

        # Create products
        for cat_name in categories:
            category = Category.objects.get(name=cat_name)
            for product_name in product_names[cat_name]:
                slug = slugify(product_name)
                # Set price between 500 and 20,000
                price = random.randint(500, 20000)
                rating = round(random.uniform(3.5, 5.0), 1)

                product, created = Product.objects.get_or_create(
                    name=product_name,
                    slug=slug,
                    category=category,
                    price=price,
                    rating=rating,
                    gst=18,
                    description=f"This is a great {product_name} in {cat_name} category."
                )
                if created:
                    # Replace placeholder with actual image if exists
                    img_path = os.path.join('store', 'static', 'store', 'images', 'products', f'{slug}.png')
                    if os.path.exists(img_path):
                        with open(img_path, 'rb') as f:
                            product.image.save(f'{slug}.png', File(f), save=True)
                    else:
                        # fallback placeholder
                        placeholder_path = os.path.join('store', 'static', 'store', 'images', 'placeholder.png')
                        with open(placeholder_path, 'rb') as f:
                            product.image.save(f'{slug}.png', File(f), save=True)

                    self.stdout.write(self.style.SUCCESS(f'Product "{product_name}" created.'))

        self.stdout.write(self.style.SUCCESS('Dummy data population completed!'))
