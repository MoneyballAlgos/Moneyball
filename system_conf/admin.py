from django.contrib import admin
from helper.common import colour
from system_conf.models import Configuration, Symbol
from admin_extra_buttons.api import ExtraButtonsMixin, button
from admin_extra_buttons.utils import HttpResponseRedirectToReferrer
from task import AccountConnection, BrokerConnection, Equity_BreakOut_1, FnO_BreakOut_1, MarketDataUpdate, SquareOff, SymbolSetup

# Register your models here.
@admin.register(Configuration)
class ConfigurationAdmin(admin.ModelAdmin):
    date_hierarchy = "created_at"
    list_display = ('product', 'amount', 'open_position', 'stoploss', 'target', 'fixed_target', 'trail_stoploss_by', 'is_active')


@admin.register(Symbol)
class SymbolAdmin(ExtraButtonsMixin, admin.ModelAdmin):
    list_display = ('fno', 'name', 'percentchange_', 'volume', 'valuechange', 'ltp', 'weekhigh52', 'weeklow52', 'strike', 'exchange', 'symbol', 'product', 'expiry', 'token', 'oi', 'lot', 'is_active')
    list_filter = ('product', 'exchange', 'fno', 'nifty50', 'nifty100', 'nifty200', 'midcpnifty50', 'midcpnifty100', 'midcpnifty150', 'smallcpnifty50', 'smallcpnifty100', 'smallcpnifty250')
    search_fields = ['name', 'symbol', 'token']

    def get_ordering(self, request):
        return ['-percentchange']
    
    def percentchange_(self, obj):
        return colour(obj.percentchange)
    percentchange_.short_description = 'Change(%)'

    # @button(change_form=True,
    #         html_attrs={'style': 'background-color:#F1502F;color:black'})
    # def Symbol_Setup(self, request):
    #     self.message_user(request, 'Symbol Setup called')
    #     SymbolSetup()
    #     self.message_user(request, 'Symbol Setup Done')
    #     return HttpResponseRedirectToReferrer(request)

    # @button(change_form=True,
    #         html_attrs={'style': 'background-color:#F1502F;color:black'})
    # def Market_Data_Update(self, request):
    #     self.message_user(request, 'Market data Update called')
    #     MarketDataUpdate()
    #     self.message_user(request, 'Market data Update Done')
    #     return HttpResponseRedirectToReferrer(request)
    
    # @button(change_form=True,
    #         html_attrs={'style': 'background-color:#F1502F;color:black'})
    # def Equity_BreakOut_1(self, request):
    #     self.message_user(request, 'Equity BreakOut 1 called')
    #     Equity_BreakOut_1(auto_trigger=False)
    #     self.message_user(request, 'Equity BreakOut 1 Done')
    #     return HttpResponseRedirectToReferrer(request)
    
    # @button(change_form=True,
    #         html_attrs={'style': 'background-color:#F1502F;color:black'})
    # def FnO_BreakOut_1(self, request):
    #     self.message_user(request, 'FnO BreakOut 1 called')
    #     FnO_BreakOut_1(auto_trigger=False)
    #     self.message_user(request, 'FnO BreakOut 1 Done')
    #     return HttpResponseRedirectToReferrer(request)
    
    # @button(change_form=True,
    #         html_attrs={'style': 'background-color:#F1502F;color:black'})
    # def Connect(self, request):
    #     self.message_user(request, 'Connect called')
    #     BrokerConnection()
    #     self.message_user(request, 'Connect Done')
    #     return HttpResponseRedirectToReferrer(request)
    
    # @button(change_form=True,
    #         html_attrs={'style': 'background-color:#F1502F;color:black'})
    # def SquareOff(self, request):
    #     self.message_user(request, 'Square Off called')
    #     SquareOff()
    #     self.message_user(request, 'Square Off Done')
    #     return HttpResponseRedirectToReferrer(request)
    
    @button(change_form=True,
            html_attrs={'style': 'background-color:#F1502F;color:black'})
    def AccountsConnection(self, request):
        self.message_user(request, 'Accounts Connection called')
        AccountConnection()
        self.message_user(request, 'Accounts Connection Done')
        return HttpResponseRedirectToReferrer(request)
