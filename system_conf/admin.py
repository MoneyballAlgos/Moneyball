from django.contrib import admin
from helper.common import colour
from system_conf.models import Configuration, Symbol

# Register your models here.
@admin.register(Configuration)
class ConfigurationAdmin(admin.ModelAdmin):
    date_hierarchy = "created_at"
    list_display = ('product', 'amount', 'open_position', 'stoploss', 'target', 'fixed_target', 'trail_stoploss_by', 'is_active')


@admin.register(Symbol)
class SymbolAdmin(admin.ModelAdmin):
    list_display = ('fno', 'name', 'percentchange_', 'ltp', 'weekhigh52', 'weeklow52', 'nifty50', 'nifty100', 'nifty200', 'midcpnifty50', 'midcpnifty100', 'midcpnifty150', 'smallcpnifty50', 'smallcpnifty100', 'smallcpnifty250', 'exchange', 'pivot', 'r1', 'r2', 'r3', 's1', 's2', 's3', 'product', 'expiry', 'strike', 'symbol', 'token', 'volume', 'valuechange', 'oi', 'lot', 'is_active')
    list_filter = ('product', 'exchange', 'fno', 'nifty50', 'nifty100', 'nifty200', 'midcpnifty50', 'midcpnifty100', 'midcpnifty150', 'smallcpnifty50', 'smallcpnifty100', 'smallcpnifty250')
    search_fields = ['name', 'symbol', 'token']

    def get_ordering(self, request):
        return ['-nifty200', '-nifty100', '-nifty50', '-midcpnifty150', '-midcpnifty100', '-midcpnifty50', '-smallcpnifty250', '-smallcpnifty100', '-smallcpnifty50', '-percentchange']
    
    def percentchange_(self, obj):
        return colour(obj.percentchange)
    percentchange_.short_description = 'Change(%)'
