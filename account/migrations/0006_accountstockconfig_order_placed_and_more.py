# Generated by Django 5.1.1 on 2024-10-08 06:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0005_delete_account_equity_status_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='accountstockconfig',
            name='order_placed',
            field=models.BooleanField(default=False, verbose_name='Ord Placed'),
        ),
        migrations.AddField(
            model_name='accounttransaction',
            name='token',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Token'),
        ),
    ]