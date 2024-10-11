from django.db import models

from system_conf.models import Symbol

# Create your models here.
class StockConfig(models.Model):
    MODES = [('CE', "Call"),
            ('PE', "Put"),
            ('none', "N/A")]
    symbol = models.ForeignKey(Symbol, on_delete=models.CASCADE)
    mode = models.CharField(max_length=50, choices=MODES, verbose_name='MODE', default='none')
    price = models.FloatField(verbose_name='PRICE', default=0)
    stoploss = models.FloatField(verbose_name='STOPLOSS', default=0)
    target = models.FloatField(verbose_name='TARGET', default=0)
    fixed_target = models.FloatField(verbose_name='Fixed Target', blank=True, null=True, default=0)
    max = models.FloatField(verbose_name='MAX GAIN', default=0)
    max_l = models.FloatField(verbose_name='MAX LOSS', default=0)
    highest_price = models.FloatField(verbose_name='HIGHEST PRICE', default=0)
    lot = models.FloatField(verbose_name='Lots', default=0)
    tr_hit = models.BooleanField(verbose_name='Target Hit', default=False)
    trailing_sl = models.FloatField(verbose_name='Trailing SL', default=0)
    ltp = models.FloatField(verbose_name='Ltp', blank=True, null=True, default=0)
    fno_activation = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.id}-{self.symbol}"


class Transaction(models.Model):
    MODES = [('CE', "Call"),
            ('PE', "Put"),
            ('none', "N/A")]
    product = models.CharField(default='equity', max_length=255, verbose_name='Product')
    symbol = models.CharField(max_length=255, verbose_name='Symbol')
    name = models.CharField(max_length=100, verbose_name='Name', blank=True, null=True)
    token = models.CharField(max_length=100, verbose_name='Token', null=True, blank=True)
    exchange = models.CharField(max_length=100, verbose_name='Exchange', null=True, blank=True)
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
    lot = models.FloatField(verbose_name='LOT')
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.id}-{self.product}-{self.symbol}"


class FnO_Status(StockConfig):
    class Meta:
        proxy = True
        verbose_name = "FnO Status"
        verbose_name_plural = "FnO Status"


class Equity_Status(StockConfig):
    class Meta:
        proxy = True
        verbose_name = "Equity Status"
        verbose_name_plural = "Equity Status"


class Equity_Transaction(Transaction):
    class Meta:
        proxy = True
        verbose_name = "Equity Transaction"
        verbose_name_plural = "Equity Transactions"


class FnO_Transaction(Transaction):
    class Meta:
        proxy = True
        verbose_name = "FnO Transaction"
        verbose_name_plural = "FnO Transactions"