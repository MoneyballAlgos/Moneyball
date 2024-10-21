from django.db import models


# Create your models here.
class AccountKeys(models.Model):
    first_name = models.CharField(max_length=200, verbose_name='First Name')
    last_name = models.CharField(max_length=200, verbose_name='Last Name')
    email = models.CharField(max_length=200, verbose_name='Email', null=True, blank=True)
    mobile = models.CharField(max_length=10, verbose_name='Mobile No.')
    api_key = models.TextField(verbose_name='Api Key', null=True, blank=True, default='please_enter_developer_api_key')
    user_id = models.CharField(max_length=100, verbose_name='User Id', null=True, blank=True, default='please_enter_angel_user_id')
    user_pin = models.CharField(max_length=50, verbose_name='Pin', null=True, blank=True, default='please_enter_angel_user_pin')
    totp_key = models.TextField(verbose_name='TOTP Key', null=True, blank=True, default='please_enter_user_totp_jey')

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name}-{self.last_name}-{self.user_id}"


class AccountConfiguration(models.Model):
    account = models.ForeignKey(AccountKeys, on_delete=models.CASCADE)
    place_order = models.BooleanField(default=False, verbose_name="Place Order")
    account_balance = models.FloatField(default=0, verbose_name="Account Balance")
    entry_amount = models.FloatField(default=5001, verbose_name="Entry Amount")
    total_open_position = models.BigIntegerField(default=20, verbose_name='Total Open Position')
    active_open_position = models.BigIntegerField(default=0, verbose_name='Active Open Position')
    equity_enabled = models.BooleanField(default=False, verbose_name='Equity-Enabled')
    fno_enabled = models.BooleanField(default=False, verbose_name='FnO-Enabled')

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.id}-{self.account.user_id}-{self.account.first_name}-{self.account.last_name}"


class AccountStockConfig(models.Model):
    MODES = [('CE', "Call"),
            ('PE', "Put"),
            ('none', "N/A")]
    account = models.ForeignKey(AccountKeys, on_delete=models.CASCADE)
    product = models.CharField(default='equity', max_length=255, verbose_name='Product')
    symbol = models.CharField(max_length=255, verbose_name='Symbol')
    name = models.CharField(max_length=100, verbose_name='Name', blank=True, null=True)
    mode = models.CharField(max_length=50, choices=MODES,verbose_name='MODE', default='none')
    lot = models.FloatField(verbose_name='Lots', default=0)
    order_id = models.CharField(max_length=255, verbose_name='ORDER ID', blank=True, null=True, default='0')
    order_placed = models.BooleanField(verbose_name='Ord Placed', default=False)
    order_status = models.TextField(verbose_name='ORDER STATUS')
    stoploss_order_placed = models.BooleanField(verbose_name='SL Ord Placed', default=False)
    stoploss_order_id = models.CharField(max_length=255, verbose_name='SL ORDER ID', blank=True, null=True, default='0')
    target_order_placed = models.BooleanField(verbose_name='TR Ord Placed', default=False)
    target_order_id = models.CharField(max_length=255, verbose_name='Tr ORDER ID', blank=True, null=True, default='0')

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
       indexes = [
            models.Index(fields=['product',]),
            ]

    def __str__(self):
        return f"{self.id}-{self.account.user_id}-{self.symbol}"


class AccountTransaction(models.Model):
    MODES = [('CE', "Call"),
            ('PE', "Put"),
            ('none', "N/A")]
    account = models.ForeignKey(AccountKeys, on_delete=models.CASCADE)
    product = models.CharField(default='equity', max_length=255, verbose_name='Product')
    symbol = models.CharField(max_length=255, verbose_name='Symbol')
    name = models.CharField(max_length=100, verbose_name='Name', blank=True, null=True)
    token = models.CharField(max_length=100, verbose_name='Token', null=True, blank=True)
    exchange = models.CharField(max_length=100, verbose_name='Exchange')
    mode = models.CharField(max_length=50, choices=MODES,verbose_name='MODE', default='none')
    indicate = models.CharField(max_length=50, verbose_name='INDICATE')
    type = models.CharField(max_length=50, verbose_name='TYPE')
    date = models.DateTimeField(auto_now_add=True)
    price = models.FloatField(verbose_name='PRICE')
    stoploss = models.FloatField(verbose_name='STOPLOSS')
    target = models.FloatField(verbose_name='TARGET')
    fixed_target = models.FloatField(verbose_name='Fixed Target', blank=True, null=True, default=0)
    profit = models.FloatField(verbose_name='PROFIT (%)', blank=True, null=True, default=0)
    max = models.FloatField(verbose_name='MAX-P (%)', blank=True, null=True, default=0)
    max_l = models.FloatField(verbose_name='MAX-L (%)', default=0)
    highest_price = models.FloatField(verbose_name='HIGHEST PRICE', default=0)
    order_id = models.CharField(max_length=255, verbose_name='ORDER ID', blank=True, null=True, default='0')
    order_status = models.TextField(verbose_name='ORDER STATUS')
    lot = models.FloatField(verbose_name='LOT')

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
       indexes = [
            models.Index(fields=['product',]),
            ]

    def __str__(self):
        return f"{self.id}-{self.account.user_id}-{self.product}-{self.symbol}"


class Account_Equity_Entry(AccountStockConfig):
    class Meta:
        proxy = True
        verbose_name = "Account Equity Entry"
        verbose_name_plural = "Account Equity Entries"


class Account_FnO_Entry(AccountStockConfig):
    class Meta:
        proxy = True
        verbose_name = "Account FnO Entry"
        verbose_name_plural = "Account FnO Entries"


class Account_Equity_Transaction(AccountTransaction):
    class Meta:
        proxy = True
        verbose_name = "Account Equity Transaction"
        verbose_name_plural = "Account Equity Transactions"


class Account_FnO_Transaction(AccountTransaction):
    class Meta:
        proxy = True
        verbose_name = "Account FnO Transaction"
        verbose_name_plural = "Account FnO Transactions"