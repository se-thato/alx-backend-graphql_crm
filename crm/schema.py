import graphene
from graphene_django.types import DjangoObjectType
from .models import Customer, Product, Order
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal
import re

from graphene_django.filter import DjangoFilterConnectionField
from .filters import CustomerFilter, ProductFilter, OrderFilter

import graphene
from crm.models import Product 

class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer

class ProductType(DjangoObjectType):
    class Meta:
        model = Product

class OrderType(DjangoObjectType):
    class Meta:
        model = Order

# Input Types
class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String() 

class ProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Decimal(required=True)
    stock = graphene.Int()

class OrderInput(graphene.InputObjectType):
    customer_id = graphene.ID(required=True)
    product_ids = graphene.List(graphene.ID, required=True)
    order_date = graphene.DateTime()

# Mutations
class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CustomerInput(required=True)

    customer = graphene.Field(CustomerType)
    message = graphene.String()
    errors = graphene.List(graphene.String)

    def mutate(self, info, input):
        errors = []
        # For Email validation
        try:
            validate_email(input.email)
        except ValidationError:
            errors.append("Invalid email format.")
        if Customer.objects.filter(email=input.email).exists():
            errors.append("Email already exists.")
        # Phone validation
        if input.phone:
            phone_pattern = r'^(\+\d{10,15}|(\d{3}-\d{3}-\d{4}))$'
            if not re.match(phone_pattern, input.phone):
                errors.append(
                    "Invalid phone format.")
        if errors:
            return CreateCustomer(customer=None, message=None, errors=errors)
        customer = Customer.objects.create(
            name=input.name,
            email=input.email,
            phone=input.phone
        )
        return CreateCustomer(customer=customer, message="Customer created successfully.", errors=None)



class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(CustomerInput, required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    def mutate(self, info, input):
        created_customers = []
        errors = []
        for idx, customer_input in enumerate(input):
            row_errors = []
            try:
                validate_email(customer_input.email)
            except ValidationError:
                row_errors.append("Invalid email format.")
            if Customer.objects.filter(email=customer_input.email).exists():
                row_errors.append("Email already exists.")
            if customer_input.phone:
                phone_pattern = r'^(\+\d{10,15}|(\d{3}-\d{3}-\d{4}))$'
                if not re.match(phone_pattern, customer_input.phone):
                    row_errors.append("Invalid phone format.")
            if row_errors:
                errors.append(f"Row {idx+1}: {', '.join(row_errors)}")
                continue
            customer = Customer.objects.create(
                name=customer_input.name,
                email=customer_input.email,
                phone=customer_input.phone
            )
            created_customers.append(customer)
        return BulkCreateCustomers(customers=created_customers, errors=errors if errors else None)



class CreateProduct(graphene.Mutation):
    class Arguments:
        input = ProductInput(required=True)

    product = graphene.Field(ProductType)
    errors = graphene.List(graphene.String)

    def mutate(self, info, input):
        errors = []
        if input.price is None or Decimal(input.price) <= 0:
            errors.append("Price must be positive.")
        if input.stock is not None and input.stock < 0:
            errors.append("Stock must be non-negative.")
        if errors:
            return CreateProduct(product=None, errors=errors)
        product = Product.objects.create(
            name=input.name,
            price=input.price,
            stock=input.stock if input.stock is not None else 0
        )
        return CreateProduct(product=product, errors=None)




class CreateOrder(graphene.Mutation):
    class Arguments:
        input = OrderInput(required=True)

    order = graphene.Field(OrderType)
    errors = graphene.List(graphene.String)

    def mutate(self, info, input):
        errors = []
        try:
            customer = Customer.objects.get(pk=input.customer_id)
        except Customer.DoesNotExist:
            errors.append("Customer does not exist.")
            return CreateOrder(order=None, errors=errors)
        if not input.product_ids or len(input.product_ids) == 0:
            errors.append("At least one product must be provided.")
            return CreateOrder(order=None, errors=errors)
        products = []
        total_amount = Decimal('0')
        for pid in input.product_ids:
            try:
                product = Product.objects.get(pk=pid)
                products.append(product)
                total_amount += product.price
            except Product.DoesNotExist:
                errors.append(f"Invalid product ID: {pid}")
        if errors:
            return CreateOrder(order=None, errors=errors)
        order = Order.objects.create(
            customer=customer,
            total_amount=total_amount,
            order_date=input.order_date or timezone.now()
        )
        order.products.set(products)
        return CreateOrder(order=order, errors=None)

class Query(graphene.ObjectType):
    all_customers = DjangoFilterConnectionField(CustomerType, filterset_class=CustomerFilter, order_by=graphene.List(of_type=graphene.String))
    all_products = DjangoFilterConnectionField(ProductType, filterset_class=ProductFilter, order_by=graphene.List(of_type=graphene.String))
    all_orders = DjangoFilterConnectionField(OrderType, filterset_class=OrderFilter, order_by=graphene.List(of_type=graphene.String))

    def resolve_all_customers(self, info, **kwargs):
        qs = Customer.objects.all()
        order_by = kwargs.get('order_by')
        if order_by:
            qs = qs.order_by(*order_by)
        return qs

    def resolve_all_products(self, info, **kwargs):
        qs = Product.objects.all()
        order_by = kwargs.get('order_by')
        if order_by:
            qs = qs.order_by(*order_by)
        return qs

    def resolve_all_orders(self, info, **kwargs):
        qs = Order.objects.all()
        order_by = kwargs.get('order_by')
        if order_by:
            qs = qs.order_by(*order_by)
        return qs


class UpdateLowStockProducts(graphene.Mutation):
    class Output(graphene.ObjectType):
        success = graphene.String()
        updated_products = graphene.List(graphene.String)

    @classmethod
    def mutate(cls, root, info):
        low_stock_products = Product.objects.filter(stock__lt=10)
        updated_names = []

        for product in low_stock_products:
            product.stock += 10
            product.save()
            updated_names.append(f"{product.name} (stock: {product.stock})")

        return UpdateLowStockProducts(
            success="Low stock products successfully restocked.",
            updated_products=updated_names
        )


class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
    update_low_stock_products = UpdateLowStockProducts.Field()

