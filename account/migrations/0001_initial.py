# Generated by Django 5.1.1 on 2024-10-05 21:04

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AccountKeys',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=200, verbose_name='First Name')),
                ('last_name', models.CharField(max_length=200, verbose_name='Last Name')),
                ('mobile', models.CharField(max_length=10, verbose_name='Mobile No.')),
                ('api_key', models.TextField(blank=True, default='please_enter_developer_api_key', null=True, verbose_name='Api Key')),
                ('user_id', models.CharField(blank=True, default='please_enter_angel_user_id', max_length=100, null=True, verbose_name='User Id')),
                ('user_pin', models.CharField(blank=True, default='please_enter_angel_user_pin', max_length=50, null=True, verbose_name='Pin')),
                ('totp_key', models.TextField(blank=True, default='please_enter_user_totp_jey', null=True, verbose_name='TOTP Key')),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='AccountConfiguration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('place_order', models.BooleanField(default=False, verbose_name='Place Order')),
                ('account_balance', models.FloatField(default=0, verbose_name='Account Balance')),
                ('entry_amount', models.FloatField(default=5001, verbose_name='Entry Amount')),
                ('total_open_position', models.BigIntegerField(default=20, verbose_name='Total Open Position')),
                ('active_open_position', models.BigIntegerField(default=0, verbose_name='Active Open Position')),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='account.accountkeys')),
            ],
        ),
        migrations.CreateModel(
            name='AccountStockConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product', models.CharField(default='equity', max_length=255, verbose_name='Product')),
                ('symbol', models.CharField(max_length=255, verbose_name='Symbol')),
                ('name', models.CharField(blank=True, max_length=100, null=True, verbose_name='Name')),
                ('mode', models.CharField(choices=[('CE', 'Call'), ('PE', 'Put'), ('none', 'N/A')], default='none', max_length=50, verbose_name='MODE')),
                ('lot', models.FloatField(default=0, verbose_name='Lots')),
                ('order_id', models.CharField(blank=True, default='0', max_length=255, null=True, verbose_name='ORDER ID')),
                ('order_status', models.TextField(verbose_name='ORDER STATUS')),
                ('stoploss_order_placed', models.BooleanField(default=False, verbose_name='SL Ord Placed')),
                ('stoploss_order_id', models.CharField(blank=True, default='0', max_length=255, null=True, verbose_name='SL ORDER ID')),
                ('target_order_placed', models.BooleanField(default=False, verbose_name='TR Ord Placed')),
                ('target_order_id', models.CharField(blank=True, default='0', max_length=255, null=True, verbose_name='Tr ORDER ID')),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='account.accountkeys')),
            ],
        ),
        migrations.CreateModel(
            name='AccountTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product', models.CharField(default='equity', max_length=255, verbose_name='Product')),
                ('symbol', models.CharField(max_length=255, verbose_name='Symbol')),
                ('name', models.CharField(blank=True, max_length=100, null=True, verbose_name='Name')),
                ('exchange', models.CharField(max_length=100, verbose_name='Exchange')),
                ('mode', models.CharField(choices=[('CE', 'Call'), ('PE', 'Put'), ('none', 'N/A')], default='none', max_length=50, verbose_name='MODE')),
                ('indicate', models.CharField(max_length=50, verbose_name='INDICATE')),
                ('type', models.CharField(max_length=50, verbose_name='TYPE')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('price', models.FloatField(verbose_name='PRICE')),
                ('stoploss', models.FloatField(verbose_name='STOPLOSS')),
                ('target', models.FloatField(verbose_name='TARGET')),
                ('fixed_target', models.FloatField(blank=True, default=0, null=True, verbose_name='Fixed Target')),
                ('profit', models.FloatField(blank=True, default=0, null=True, verbose_name='PROFIT (%)')),
                ('max', models.FloatField(blank=True, default=0, null=True, verbose_name='MAX-P (%)')),
                ('max_l', models.FloatField(default=0, verbose_name='MAX-L (%)')),
                ('highest_price', models.FloatField(default=0, verbose_name='HIGHEST PRICE')),
                ('order_id', models.CharField(blank=True, default='0', max_length=255, null=True, verbose_name='ORDER ID')),
                ('order_status', models.TextField(verbose_name='ORDER STATUS')),
                ('lot', models.FloatField(verbose_name='LOT')),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='account.accountkeys')),
            ],
        ),
    ]