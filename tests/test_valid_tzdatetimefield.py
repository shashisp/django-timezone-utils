# ==============================================================================
# IMPORTS
# ==============================================================================
# Python
from datetime import datetime

import pytz


# Django
from django.conf import settings
from django.test import TestCase
from django.utils.timezone import make_aware


# App
from tests.models import TZWithGoodStringDefault
from .models import (ModelWithDateTimeOnly,
                                                CallableTimeStampedModel,
                                                StaticTimeStampedModel,
                                                ModelWithForeignKeyToTimeZone,
                                                NullModelWithDateTimeOnly,
                                                ModelWithLocalTimeZone,
                                                ModelWithLocalTZCharField)


# ==============================================================================
# TESTS: Valid ateTimeWithTimeZoneField
# ==============================================================================
class DateTimeWithTimeZoneFieldTestCase(TestCase):
    def setUp(self):
        ModelWithDateTimeOnly.objects.create()
        CallableTimeStampedModel.objects.create()
        StaticTimeStampedModel.objects.create()
        NullModelWithDateTimeOnly.objects.create()
        ModelWithLocalTimeZone.objects.create()

        location = TZWithGoodStringDefault.objects.create()
        ModelWithForeignKeyToTimeZone.objects.create(other_model=location)

    def test_that_model_timestamp_is_unaltered(self):
        """Make sure that we aren't modifying the timezone if one is not
        provided.

        """
        model_instance = ModelWithDateTimeOnly.objects.get()
        self.assertEquals(
            model_instance.timestamp,
            settings.TEST_DATETIME
        )

    def test_callable_timestamp_time_override(self):
        model_instance = CallableTimeStampedModel.objects.get()
        self.assertEquals(
            model_instance.start.astimezone(pytz.timezone(settings.TIME_ZONE)).time(),
            datetime.min.time(),
            'Start time does not match datetime.min.time().'
        )
        self.assertEquals(
            model_instance.end.astimezone(pytz.timezone(settings.TIME_ZONE)).time(),
            datetime.max.time(),
            'End time does not match datetime.max.time().'
        )

    def test_datetime_time_timestamp_override(self):
        model_instance = StaticTimeStampedModel.objects.get()
        tz = pytz.timezone(settings.TIME_ZONE)
        start_time = tz.normalize(make_aware(datetime(2014, 1, 1, 0, 0, 0, 0), tz))
        end_time = tz.normalize(make_aware(datetime(2014, 1, 1, 23, 59, 59, 999999), tz))

        self.assertEquals(
            model_instance.start,
            start_time,
            'Start time does not match datetime.min.time(): ({0} != {1})'.format(
                repr(model_instance.start),
                repr(start_time)
            )
        )
        self.assertEquals(
            model_instance.end,
            end_time,
            'End time does not match datetime.max.time(): ({0} != {1})'.format(
                repr(model_instance.end),
                repr(end_time)
            )
        )

    def test_populate_from_foreignkey_timezone(self):
        model_instance = ModelWithForeignKeyToTimeZone.objects.get()

        self.assertEqual(
            model_instance.timestamp,
            settings.TEST_DATETIME,
        )

    def test_populate_from_local_timezone(self):
        model_instance = ModelWithLocalTimeZone.objects.get()

        self.assertEqual(
            model_instance.timestamp,
            settings.TEST_DATETIME,
        )

    def test_populate_from_local_timezone_charfield(self):
        model_instance = ModelWithLocalTZCharField.objects.create()

        self.assertEqual(
            model_instance.timestamp,
            settings.TEST_DATETIME
        )
