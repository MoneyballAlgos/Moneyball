from datetime import timedelta
from django.contrib import admin
from helper.common import colour
from import_export.admin import ExportActionMixin
from account.models import AccountKeys, AccountConfiguration, AccountStockConfig, AccountTransaction, Account_Equity_Transaction, Account_FnO_Transaction, Account_Equity_Status, Account_FnO_Status


# Register your models here.
@admin.register(AccountKeys)
class AccountKeyAdmin(ExportActionMixin, admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'mobile', 'api_key', 'user_id', 'user_pin', 'totp_key', 'is_active')
    search_fields = ['first_name', 'last_name', 'mobile', 'user_id']
    list_filter = ('is_active',)


@admin.register(AccountConfiguration)
class AccountConfigurationAdmin(ExportActionMixin, admin.ModelAdmin):
    list_display = ('account_name', 'place_order', 'account_balance', 'entry_amount', 'equity_enabled', 'fno_enabled', 'total_open_position', 'active_open_position', 'is_active')
    search_fields = ['account__first_name', 'account__last_name', 'account__mobile', 'account__user_id']
    list_filter = ('account__first_name', 'is_active')

    def account_name(self, obj):
        return f"{obj.account.first_name}"# {obj.account.last_name[0]}"
    account_name.short_description = 'User'

@admin.register(AccountStockConfig)
class AccountStockConfigAdmin(ExportActionMixin, admin.ModelAdmin):
    list_display = ('account_name', 'created_at', 'product', 'symbol', 'name', 'mode', 'lot', 'order_id', 'order_status', 'stoploss_order_placed', 'target_order_placed', 'stoploss_order_id', 'target_order_id', 'is_active')
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
    list_display = ('account_name', 'symbol', 'date', 'indicate', 'type', 'p_l', 'max_p', 'max_l_s', 'top_p', 'price', 'fixed_target', 'stoploss', 'target', 'lot', 'order_id', 'order_status', 'name', 'exchange', 'mode')
    search_fields = ['symbol', ]
    list_filter = ('account__first_name', 'indicate', 'date', 'mode', 'name')
    list_per_page = 20

    def get_queryset(self, request):
        return self.model.objects.filter(product='equity')

    def get_ordering(self, request):
        return ['-date']
    
    def account_name(self, obj):
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


@admin.register(Account_Equity_Status)
class AccountEquityStatusAdmin(ExportActionMixin, admin.ModelAdmin):
    list_display = ('account_name', 'entry_time', 'symbol', 'name', 'mode', 'lot', 'stoploss_order_placed', 'target_order_placed', 'is_active')
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


@admin.register(Account_FnO_Status)
class AccountFnOStatusAdmin(ExportActionMixin, admin.ModelAdmin):
    list_display = ('account_name', 'entry_time', 'symbol', 'name', 'mode', 'lot', 'stoploss_order_placed', 'target_order_placed', 'is_active')
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