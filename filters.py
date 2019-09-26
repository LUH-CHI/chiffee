import django_filters

from chiffee.models import Buy


class BuyFilter(django_filters.FilterSet):
    buy_date = django_filters.DateRangeFilter(label='Date of purchase:',
                                              field_name='buy_date')
    buy_date_range = django_filters.DateFromToRangeFilter(
        label='Date of purchase (range):',
        field_name='buy_date')

    class Meta:
        model = Buy
        fields = ['buy_user', 'buy_product', 'buy_date', 'buy_date_range']
