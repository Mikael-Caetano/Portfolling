from django import forms

#Modified widget to Filefield
class NamedFileInput(forms.ClearableFileInput):
    template_name = 'widgets/NamedFileInput.html'

#Modified widget to use HTML date input
class DatePicker(forms.DateInput):
    input_type = 'date'
    
