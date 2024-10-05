from django.contrib import admin
from helper.common import colour
from import_export.admin import ExportActionMixin
from account.models import AccountKeys, AccountConfiguration, AccountStockConfig, AccountTransaction


# Register your models here.
@admin.register(AccountKeys)
class AccountKeyAdmin(ExportActionMixin, admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'mobile', 'api_key', 'user_id', 'user_pin', 'totp_key', 'is_active')
    search_fields = ['first_name', 'last_name', 'mobile', 'user_id']
    list_filter = ('is_active',)


@admin.register(AccountConfiguration)
class AccountConfigurationAdmin(ExportActionMixin, admin.ModelAdmin):
    list_display = ('account', 'place_order', 'account_balance', 'entry_amount', 'total_open_position', 'active_open_position', 'is_active')
    search_fields = ['account__first_name', 'account__last_name', 'account__mobile', 'account__user_id']
    list_filter = ('account__first_name', 'is_active')


@admin.register(AccountStockConfig)
class AccountStockConfigAdmin(ExportActionMixin, admin.ModelAdmin):
    list_display = ('account', 'created_at', 'product', 'symbol', 'name', 'mode', 'lot', 'order_id', 'order_status', 'stoploss_order_placed', 'target_order_placed', 'stoploss_order_id', 'target_order_id', 'is_active')
    search_fields = ['account__first_name', 'account__last_name', 'account__mobile', 'account__user_id']
    list_filter = ('account__first_name', 'is_active')

    def get_ordering(self, request):
        return ['-created_at']


@admin.register(AccountTransaction)
class AccountTransactionAdmin(ExportActionMixin, admin.ModelAdmin):
    date_hierarchy = 'date'
    list_display = ('account', 'product', 'symbol', 'date', 'indicate', 'type', 'p_l', 'max_p', 'max_l_s', 'top_p', 'price', 'fixed_target', 'stoploss', 'target', 'lot', 'order_id', 'order_status', 'name', 'exchange', 'mode')
    search_fields = ['account__first_name', 'account__last_name', 'account__mobile', 'account__user_id']
    list_filter = ('account__first_name', 'product', 'indicate', 'date', 'mode', 'name', 'is_active')

    def get_ordering(self, request):
        return ['-date']
    
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
