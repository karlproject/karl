from convertish.convert import ConvertError
from convertish.convert import Converter
from convertish.convert import string_converter
from datetime import datetime
from karl.views.forms.attr import KarlDateTime

_default_datetime_format = '%m/%d/%Y %H:%M'
class KarlDateTimeToStringConverter(Converter):
    round_minutes = 15

    def from_type(self, value, converter_options={}):
        datetime_format = converter_options.get('datetime_format', _default_datetime_format)
        if value is None:
            return None
        value = self._round_datetime(value)
        return value.strftime(datetime_format)

    def to_type(self, value, converter_options={}):
        datetime_format = converter_options.get('datetime_format', _default_datetime_format)
        try: 
            result = datetime.strptime(value, datetime_format)
        except ValueError, e:
            raise ConvertError('Invalid date: ' + str(e))
        return result

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
