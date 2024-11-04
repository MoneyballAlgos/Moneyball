from datetime import timedelta
from django.contrib import admin
from helper.common import colour
from stock.models import StockConfig
from django.utils.html import format_html
from import_export.admin import ExportActionMixin
from account.models import Account_Equity_Portfolio, AccountKeys, AccountConfiguration, AccountStockConfig, AccountTransaction, Account_Equity_Transaction, Account_FnO_Transaction, Account_Equity_Entry, Account_FnO_Entry


# Register your models here.
@admin.register(AccountKeys)
class AccountKeyAdmin(ExportActionMixin, admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'mobile', 'email', 'api_key', 'user_id', 'user_pin', 'totp_key', 'is_active')
    search_fields = ['first_name', 'last_name', 'mobile', 'user_id']
    list_filter = ('is_active',)


@admin.register(AccountConfiguration)
class AccountConfigurationAdmin(admin.ModelAdmin):
    list_display = ('account_name', 'place_order', 'account_balance', 'entry_amount', 'total_open_position', 'active_open_position', 'fno_enabled', 'equity_enabled', 'indics', 'is_active')
    search_fields = ['account__first_name', 'account__last_name', 'account__mobile', 'account__user_id']
    list_filter = ('account__first_name', 'nifty50', 'nifty100', 'nifty200', 'midcpnifty50', 'midcpnifty100', 'midcpnifty150', 'smallcpnifty50', 'smallcpnifty100', 'smallcpnifty250', 'is_active')

    def account_name(self, obj):
        return f"{obj.account.first_name}"# {obj.account.last_name[0]}"
    account_name.short_description = 'User'

    def indics(self, obj):
        ind_str = []
        if obj.nifty50:
            ind_str.append('N50')
        if obj.nifty100:
            ind_str.append('N100')
        if obj.nifty200:
            ind_str.append('N200')
        if obj.midcpnifty50:
            ind_str.append('MDCP50')
        if obj.midcpnifty100:
            ind_str.append('MDCP100')
        if obj.midcpnifty150:
            ind_str.append('MDCP150')
        if obj.smallcpnifty50:
            ind_str.append('SMCP50')
        if obj.smallcpnifty100:
            ind_str.append('SMCP100')
        if obj.smallcpnifty250:
            ind_str.append('SMCP250')
        return "-".join(ind_str)
    indics.short_description = 'Enabled-Indics'

@admin.register(AccountStockConfig)
class AccountStockConfigAdmin(admin.ModelAdmin):
    list_display = ('account_name', 'created_at', 'product', 'symbol', 'name', 'mode', 'lot', 'order_id', 'order_placed', 'stoploss_order_placed', 'target_order_placed', 'stoploss_order_id', 'target_order_id', 'order_status', 'is_active')
    search_fields = ['account__first_name', 'account__last_name', 'account__mobile', 'account__user_id']
    list_filter = ('account__first_name', 'is_active')

    def get_ordering(self, request):
        return ['-created_at']

    def account_name(self, obj):
        return f"{obj.account.first_name}"# {obj.account.last_name[0]}"
    account_name.short_description = 'User'

@admin.register(AccountTransaction)
class AccountTransactionAdmin(ExportActionMixin, admin.ModelAdmin):
    date_hierarchy = 'date'
    list_display = ('account_name', 'product', 'symbol', 'date', 'indicate', 'type', 'p_l', 'max_p', 'max_l_s', 'top_p', 'price', 'fixed_target', 'stoploss', 'target', 'lot', 'order_id', 'order_status', 'name', 'exchange', 'mode')
    search_fields = ['account__first_name', 'account__last_name', 'account__mobile', 'account__user_id']
    list_filter = ('account__first_name', 'product', 'indicate', 'date', 'mode', 'name', 'is_active')

    def get_ordering(self, request):
        return ['-date']

    def account_name(self, obj):
        if 'Cancelled' in obj.order_status:
            return format_html('<strong style="color:Orange;">{}</strong>', f"{obj.account.first_name}")
        return f"{obj.account.first_name}"# {obj.account.last_name[0]}"
    account_name.short_description = 'User'

    def top_p(self, obj):
        if obj.indicate == "ENTRY":
            return ''
        else:
            return obj.highest_price
    top_p.short_description = 'Top Price'

    def max_p(self, obj):
        if obj.indicate == "ENTRY":
            return ''
        else:
            return colour(obj.max)
    max_p.short_description = 'Max-P%'
    
    def max_l_s(self, obj):
        if obj.indicate == "ENTRY":
            return ''
        else:
            return colour(obj.max_l)
    max_l_s.short_description = 'Max-L%'
    
    def p_l(self, obj):
        if obj.indicate == "ENTRY":
            return ''
        else:
            return colour(obj.profit)
    p_l.short_description = 'Profit-%'

@admin.register(Account_Equity_Transaction)
class AccountEquityTransactionAdmin(ExportActionMixin, admin.ModelAdmin):
    date_hierarchy = 'date'
    list_display = ('account_name', 'name', 'date', 'indicate', 'type', 'p_l', 'max_p', 'max_l_s', 'top_p', 'price', 'fixed_target', 'stoploss', 'target', 'lot', 'order_id', 'order_status', 'symbol', 'exchange', 'mode')
    search_fields = ['symbol', ]
    list_filter = ('account__first_name', 'indicate', 'date', 'mode', 'name')
    list_per_page = 20

    def get_queryset(self, request):
        return self.model.objects.filter(product='equity')

    def get_ordering(self, request):
        return ['-date']
    
    def account_name(self, obj):
        if 'Cancelled' in obj.order_status:
            return format_html('<strong style="color:Orange;">{}</strong>', f"{obj.account.first_name}")
        return f"{obj.account.first_name}"# {obj.account.last_name[0]}"
    account_name.short_description = 'User'

    def top_p(self, obj):
        if obj.indicate == "ENTRY":
            return ''
        else:
            return obj.highest_price
    top_p.short_description = 'Top Price'

    def max_p(self, obj):
        if obj.indicate == "ENTRY":
            return ''
        else:
            return colour(obj.max)
    max_p.short_description = 'Max-P%'
    
    def max_l_s(self, obj):
        if obj.indicate == "ENTRY":
            return ''
        else:
            return colour(obj.max_l)
    max_l_s.short_description = 'Max-L%'
    
    def p_l(self, obj):
        if obj.indicate == "ENTRY":
            return ''
        else:
            return colour(obj.profit)
    p_l.short_description = 'Profit-%'


@admin.register(Account_FnO_Transaction)
class AccountFnOTransactionAdmin(ExportActionMixin, admin.ModelAdmin):
    date_hierarchy = 'date'
    list_display = ('account_name', 'symbol', 'date', 'indicate', 'type', 'p_l', 'max_p', 'max_l_s', 'top_p', 'price', 'fixed_target', 'stoploss', 'target', 'lot', 'order_id', 'order_status', 'name', 'exchange', 'mode')
    search_fields = ['symbol', ]
    list_filter = ('account__first_name', 'indicate', 'date', 'mode', 'name')
    list_per_page = 20

    def get_queryset(self, request):
        return self.model.objects.filter(product='future')

    def get_ordering(self, request):
        return ['-date']
    
    def account_name(self, obj):
        if 'Cancelled' in obj.order_status:
            return format_html('<strong style="color:Orange;">{}</strong>', f"{obj.account.first_name}")
        return f"{obj.account.first_name}"# {obj.account.last_name[0]}"
    account_name.short_description = 'User'

    def top_p(self, obj):
        if obj.indicate == "ENTRY":
            return ''
        else:
            return obj.highest_price
    top_p.short_description = 'Top Price'

    def max_p(self, obj):
        if obj.indicate == "ENTRY":
            return ''
        else:
            return colour(obj.max)
    max_p.short_description = 'Max-P%'
    
    def max_l_s(self, obj):
        if obj.indicate == "ENTRY":
            return ''
        else:
            return colour(obj.max_l)
    max_l_s.short_description = 'Max-L%'
    
    def p_l(self, obj):
        if obj.indicate == "ENTRY":
            return ''
        else:
            return colour(obj.profit)
    p_l.short_description = 'Profit-%'


@admin.register(Account_Equity_Entry)
class AccountEquityEntryAdmin(admin.ModelAdmin):
    list_display = ('account_name', 'entry_time', 'name', 'mode', 'lot', 'order_placed', 'stoploss_order_placed', 'target_order_placed', 'symbol', 'order_status', 'is_active')
    search_fields = ['account__first_name', 'account__last_name', 'account__mobile', 'account__user_id']
    list_filter = ('account__first_name', 'is_active')

    def get_queryset(self, request):
        return self.model.objects.filter(product='equity')

    def get_ordering(self, request):
        return ['-created_at']

    def account_name(self, obj):
        return f"{obj.account.first_name}"# {obj.account.last_name[0]}"
    account_name.short_description = 'User'

    def entry_time(self, obj):
        return (obj.created_at + timedelta(hours=5, minutes=30)).strftime("%d/%m/%y %-I:%-M:%-S %p")
    entry_time.short_description = 'Time'


@admin.register(Account_FnO_Entry)
class AccountFnOEntryAdmin(admin.ModelAdmin):
    list_display = ('account_name', 'entry_time', 'symbol', 'mode', 'lot', 'order_placed', 'stoploss_order_placed', 'target_order_placed', 'name', 'order_status', 'is_active')
    search_fields = ['account__first_name', 'account__last_name', 'account__mobile', 'account__user_id']
    list_filter = ('account__first_name', 'is_active')

    def get_queryset(self, request):
        return self.model.objects.filter(product='future')

    def get_ordering(self, request):
        return ['-created_at']

    def account_name(self, obj):
        return f"{obj.account.first_name}"# {obj.account.last_name[0]}"
    account_name.short_description = 'User'

    def entry_time(self, obj):
        return (obj.created_at + timedelta(hours=5, minutes=30)).strftime("%-I:%-M:%-S %p")
    entry_time.short_description = 'Time'


@admin.register(Account_Equity_Portfolio)
class AccountEquityPortfolioAdmin(admin.ModelAdmin):
    list_display = ('account_name', 'pnl', 'current', 'investment')
    search_fields = ['first_name', 'last_name', 'mobile', 'user_id']
    list_per_page = 10

    def account_name(self, obj):
        return f"{obj.user_id} ({obj.first_name})"
    account_name.short_description = 'User'

    def investment(self, obj):
        invested_value = 0
        entries = AccountStockConfig.objects.filter(account=obj)
        for i in entries:
            stock_obj = StockConfig.objects.get(symbol__symbol=i.symbol)
            invested_value += i.lot * stock_obj.price
        return round(invested_value, 2)
    investment.short_description = 'Investment (₹)'
    
    def current(self, obj):
        current_value = 0
        entries = AccountStockConfig.objects.filter(account=obj)
        for i in entries:
            stock_obj = StockConfig.objects.get(symbol__symbol=i.symbol)
            current_value += i.lot * stock_obj.ltp
        return round(current_value, 2)
    current.short_description = 'Current (₹)'
    
    def pnl(self, obj):
        invested_value = 0
        current_value = 0
        entries = AccountStockConfig.objects.filter(account=obj)
        for i in entries:
            stock_obj = StockConfig.objects.get(symbol__symbol=i.symbol)
            current_value += i.lot * stock_obj.ltp
            invested_value += i.lot * stock_obj.price
        pnl = round((current_value - invested_value)/invested_value * 100, 2)
        return colour(pnl)
    pnl.short_description = 'P/L (%)'