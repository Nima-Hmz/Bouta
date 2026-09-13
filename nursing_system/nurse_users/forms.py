# File: forms.py
from django_flatpickr.widgets import TimePickerInput
from django_flatpickr.schemas import FlatpickrOptions
from django.contrib.gis import forms as gis_forms
from .models import NurseLocation
from .models import WorkingHours
from django import forms

# working hours form (using django_flatpickr)
class WorkingHoursForm(forms.ModelForm):
    class Meta:
        model = WorkingHours
        fields = ['start_time', 'end_time', 'day']
        widgets = {
            'start_time': TimePickerInput(
                options=FlatpickrOptions(
                    time_24hr=True,   # Uses 24-hour format instead of AM/PM
                    altFormat="H:i",    # Time format (HH:mm)
                )
            ),
            'end_time': TimePickerInput(
                            options=FlatpickrOptions(
                                time_24hr=True,   # Uses 24-hour format instead of AM/PM
                                altFormat="H:i",    # Time format (HH:mm)
                            )
                        ),
        }
        labels = {
            'start_time':'ساعت شروع کار',
            'end_time':'ساعت پایان کار',
            'day':'روز کاری'
        }

class NurseLocationForm(forms.ModelForm):
    location = gis_forms.PointField(widget=gis_forms.OSMWidget(attrs={
        'map_width': 600,
        'map_height': 400,
    }))

    class Meta:
        model = NurseLocation
        fields = ['location']

        labels = {
            'location':'موقعیت پرستار',
        }

        
