from convertish.convert import ConvertError
from convertish.convert import Converter
from convertish.convert import string_converter
from datetime import datetime
from karl.views.forms.attr import KarlDateTime

class KarlDateTimeToStringConverter(Converter):
    datetime_format = '%m/%d/%Y %H:%M'
    round_minutes = 15

    def from_type(self, value, converter_options={}):
        if value is None:
            return None
        value = self._round_datetime(value)
        return value.strftime(self.datetime_format)

    def to_type(self, value, converter_options={}):
        try:
            date, time = value.split()
            month, day, year = [int(p) for p in date.split('/')]
            hour, minute = [int(p) for p in time.split(':')]
        except ValueError, e:
            raise ConvertError('Invalid date: ' + str(e))
        return datetime(year, month, day, hour, minute)

    def _round_datetime(self, ts):
        """Round the datetime to quarters of hours"""
        round_minutes = self.round_minutes
        rounded_ts = ts.replace(
            minute = ts.minute / round_minutes * round_minutes,
            second = 0,
            microsecond = 0,
            )
        return rounded_ts

@string_converter.when_type(KarlDateTime)
def datetime_to_string(schema_type):
    return KarlDateTimeToStringConverter(schema_type)
