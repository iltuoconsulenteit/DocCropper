import os
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django

def run():
    django.setup()
    from platform.apps.licenses.models import Customer, Product, License

    customer, _ = Customer.objects.get_or_create(name='Demo Customer', email='demo@example.com')
    product, _ = Product.objects.get_or_create(name='Demo Product')
    License.objects.get_or_create(key='DEMO-KEY', customer=customer, product=product)


if __name__ == '__main__':
    run()
