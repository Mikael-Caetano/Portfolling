from django import forms

class NamedFileInput(forms.ClearableFileInput):
    """
    Custom file input without a clear button but with the uploaded file name being shown correctly.
    """
    template_name = 'widgets/NamedFileInput.html'

class DatePicker(forms.DateInput):
    """
    Modified widget to use HTML date input
    """
    input_type = 'date'
    
