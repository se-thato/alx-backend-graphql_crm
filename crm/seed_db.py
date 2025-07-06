from .models import Customer, Product

def seed():
    Customer.objects.create(name="Test User", email="test@example.com", phone="+1234567890")
    Product.objects.create(name="Sample Product", price=100, stock=5)