from zoneinfo import ZoneInfo
from django.contrib import admin
from datetime import timedelta, datetime
from import_export.admin import ExportActionMixin
from helper.common import colour, colour_indicator
from admin_extra_buttons.api import ExtraButtonsMixin, button
from admin_extra_buttons.utils import HttpResponseRedirectToReferrer
from stock.models import StockConfig, Transaction, FnO_Status, Equity_Status, FnO_Transaction, Equity_Transaction


# Register your models here.
@admin.register(FnO_Status)
class FnOStatusAdmin(ExtraButtonsMixin, admin.ModelAdmin):
    # actions = None
    list_display = ('entry_time', 'name_', 'current', 'max_p', 'max_l_s', 'ltp', 'fixed_target', 'price', 'stoploss', 'trailing_sl', 'target', 'highest_price', 'lot', 'tr_hit', 'mode', 'product')

    def has_add_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        return self.model.objects.filter(symbol__product='future')
    
    def product(self, obj):
        return f"{obj.symbol.product}"
    product.short_description = 'Product'

    def name_(self, obj):
        if obj.symbol.product == 'future':
            return f"{obj.symbol.name}-{obj.symbol.strike}-{obj.symbol.symbol[-2:]}"
        else:
            return f"{obj.symbol.name}"
    name_.short_description = 'Name'
    
    def entry_time(self, obj):
        return (obj.created_at + timedelta(hours=5, minutes=30)).strftime("%-I:%-M:%-S %p")
    entry_time.short_description = 'Time'

    def max_p(self, obj):
        return colour(round(obj.max, 2))
    max_p.short_description = 'Max-P%'
    
    def max_l_s(self, obj):
        return colour(round(obj.max_l, 2))
    max_l_s.short_description = 'Max-L%'

    def current(self, obj):
        return colour_indicator(obj, obj.ltp)


    @button(change_form=True,
            html_attrs={'style': 'background-color:#15FBF1;color:black'})
    def STATUS(self, request):
        now = datetime.now(tz=ZoneInfo("Asia/Kolkata"))
        future_total_exit = Transaction.objects.filter(product='future', indicate='EXIT', is_active=True).order_by('date').count()
        future_total_entry = Transaction.objects.filter(product='future', indicate='ENTRY', is_active=True).order_by('date').count()
        future_accuracy = round((len(Transaction.objects.filter(product='future', profit__gte=0, indicate='EXIT', is_active=True))/future_total_exit) * 100, 2) if future_total_exit != 0 else 0
        future_till_now = round(sum(Transaction.objects.filter(product='future', indicate='EXIT', is_active=True).values_list('profit', flat=True)), 2)
        future_today_exit = Transaction.objects.filter(date__date=now.date(), product='future', indicate='EXIT', is_active=True).order_by('date').count()
        future_today_entry = Transaction.objects.filter(date__date=now.date(), product='future', indicate='ENTRY', is_active=True).order_by('date').count()
        future_today = round(sum(Transaction.objects.filter(date__date=now.date(), product='future', indicate='EXIT', is_active=True).values_list('profit', flat=True)), 2)
        self.message_user(request, f'Total: Entry: {future_total_entry}, Exit: {future_total_exit}.')
        self.message_user(request, f'--- {future_accuracy} % Accuracy on {future_total_exit} Trades ---')
        self.message_user(request, f'Today: Entry: {future_today_entry}, Exit: {future_today_exit}.')
        self.message_user(request, f'--- Gained {future_today} % today, {future_till_now} % till now ---')
        return HttpResponseRedirectToReferrer(request)


@admin.register(Equity_Status)
class EquityStatusAdmin(ExtraButtonsMixin, admin.ModelAdmin):
    # actions = None
    list_display = ('entry_time', 'name_', 'current', 'max_p', 'max_l_s', 'ltp', 'fixed_target', 'price', 'stoploss', 'trailing_sl', 'target', 'highest_price', 'indics', 'lot', 'tr_hit', 'mode', 'product')

    def has_add_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        return self.model.objects.filter(symbol__product='equity')
    
    def indics(self, obj):
        ind_str = []
        if obj.symbol.nifty50:
            ind_str.append('N50')
        if obj.symbol.nifty100:
            ind_str.append('N100')
        if obj.symbol.nifty200:
            ind_str.append('N200')
        if obj.symbol.midcpnifty50:
            ind_str.append('MDCP50')
        if obj.symbol.midcpnifty100:
            ind_str.append('MDCP100')
        if obj.symbol.midcpnifty150:
            ind_str.append('MDCP150')
        if obj.symbol.smallcpnifty50:
            ind_str.append('SMCP50')
        if obj.symbol.smallcpnifty100:
            ind_str.append('SMCP100')
        if obj.symbol.smallcpnifty250:
            ind_str.append('SMCP250')
        return ",".join(ind_str)
    indics.short_description = 'Indics'

    def product(self, obj):
        return f"{obj.symbol.product}"
    product.short_description = 'Product'

    def name_(self, obj):
        if obj.symbol.product == 'future':
            return f"{obj.symbol.name}-{obj.symbol.strike}-{obj.symbol.symbol[-2:]}"
        else:
            return f"{obj.symbol.name}"
    name_.short_description = 'Name'
    
    def entry_time(self, obj):
        return (obj.created_at + timedelta(hours=5, minutes=30)).strftime("%d/%m/%y %-I:%-M:%-S %p")
    entry_time.short_description = 'Time'

    def max_p(self, obj):
        return colour(round(obj.max, 2))
    max_p.short_description = 'Max-P%'
    
    def max_l_s(self, obj):
        return colour(round(obj.max_l, 2))
    max_l_s.short_description = 'Max-L%'

    def current(self, obj):
        return colour_indicator(obj, obj.ltp)

    @button(change_form=True,
            html_attrs={'style': 'background-color:#15FBF1;color:black'})
    def STATUS(self, request):
        equity_total_exit = Transaction.objects.filter(product='equity', indicate='EXIT', is_active=True).order_by('date').count()
        equity_total_entry = Transaction.objects.filter(product='equity', indicate='ENTRY', is_active=True).order_by('date').count()
        equity_accuracy = round((len(Transaction.objects.filter(product='equity', profit__gte=0, indicate='EXIT', is_active=True))/equity_total_exit) * 100, 2) if equity_total_exit != 0 else 0
        equity_till_now = round(sum(Transaction.objects.filter(product='equity', indicate='EXIT', is_active=True).values_list('profit', flat=True)), 2)

        self.message_user(request, f'Total: Entry: {equity_total_entry}, Exit: {equity_total_exit}.')
        self.message_user(request, f'--- {equity_accuracy} % Accuracy on {equity_total_exit} Trades ---')
        self.message_user(request, f'--- Gained: {equity_till_now} % till now ---')
        return HttpResponseRedirectToReferrer(request)


@admin.register(FnO_Transaction)
class FnOTransactionAdmin(ExportActionMixin, admin.ModelAdmin):
    date_hierarchy = 'date'
    list_display = ('symbol', 'date', 'indicate', 'type', 'p_l', 'max_p', 'max_l_s', 'top_p', 'price', 'fixed_target', 'stoploss', 'target', 'lot', 'name', 'token', 'exchange', 'mode')
    search_fields = ['symbol', ]
    list_filter = ('indicate', 'date', 'mode', 'name')
    list_per_page = 20

    def get_queryset(self, request):
        return self.model.objects.filter(product='future')

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


@admin.register(Equity_Transaction)
class EquityTransactionAdmin(ExportActionMixin, admin.ModelAdmin):
    date_hierarchy = 'date'
    list_display = ('name', 'date', 'indicate', 'type', 'p_l', 'max_p', 'max_l_s', 'top_p', 'price', 'fixed_target', 'stoploss', 'target', 'lot', 'symbol', 'token', 'exchange', 'mode')
    search_fields = ['symbol', ]
    list_filter = ('indicate', 'date', 'mode', 'name')
    list_per_page = 20

    def get_queryset(self, request):
        return self.model.objects.filter(product='equity')

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


@admin.register(StockConfig)
class StockConfigAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'mode', 'symbol__name', 'ltp', 'tr_hit', 'trailing_sl', 'max', 'max_l', 'price', 'target', 'stoploss', 'fixed_target', 'highest_price', 'symbol__symbol', 'lot', 'is_active')
    search_fields = ['symbol', ]

    def get_ordering(self, request):
        return ['-created_at']


@admin.register(Transaction)
class TransactionAdmin(ExportActionMixin, admin.ModelAdmin):
    date_hierarchy = 'date'
    list_display = ('product', 'symbol', 'date', 'indicate', 'type', 'p_l', 'max_p', 'max_l_s', 'top_p', 'price', 'fixed_target', 'stoploss', 'target', 'lot', 'name', 'token', 'exchange', 'mode')
    search_fields = ['symbol', ]
    list_filter = ('product', 'indicate', 'date', 'mode', 'name')
    list_per_page = 20

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
