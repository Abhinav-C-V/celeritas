# Generated by Django 4.2.2 on 2023-07-17 16:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0002_remove_cartitem_cart_remove_cartitem_product_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='stock',
        ),
    ]
