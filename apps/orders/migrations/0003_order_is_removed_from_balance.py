# Generated by Django 5.0.7 on 2024-08-08 09:17

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("orders", "0002_rename_total_order_total_price"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="is_removed_from_balance",
            field=models.BooleanField(default=False),
        ),
    ]
