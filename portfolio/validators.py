from django.core.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
from django.utils import timezone, dateformat


def validate_file_size(file):
    """
    Validate that the file size is less than 5 MB.
    """
    filesize = file.size
    
    if filesize > 5242880:
        raise ValidationError("The maximum file size that can be uploaded is 5MB")
    else:
        return file

def validate_project_name(project_name):
    """
    Validate that `project_name` contains only allowed characters.
    """
    valid_characters = r"-_ ~"
    for char in project_name:
        if char in valid_characters or char.isalnum():
            continue
        raise ValidationError("Enter a valid project name. This value may contain only letters, numbers, and -/_/ /~, characters.")
    return project_name

def validate_birthdate(birthdate):
    """
    Validate that `birthdate` is in a range from 120 years ago to the present day.
    """
    birthdate = dateformat.format(birthdate, 'Y-m-d')
    now = dateformat.format(timezone.now(), 'Y-m-d')
    min_date = dateformat.format(timezone.now() - relativedelta(years=120), 'Y-m-d')
    if min_date <= birthdate <= now:
        return birthdate
    raise ValidationError(f"Enter a valid birthdate. This value must be in the interval [{min_date}]-[{now}]")
