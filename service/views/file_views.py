# views.py
from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
import os
import posixpath

# BUG починить отображение прикрепленных файлов 

def file_view(request, file_path):
    # Build the absolute path to the file
    file_path = posixpath.normpath(file_path)
    print(f"File path received: {file_path}")
    file_absolute_path = os.path.join(posixpath.normpath(settings.MEDIA_ROOT), file_path)
    print(settings.MEDIA_ROOT)
    print(file_absolute_path)
    # Check if the file exists
    if os.path.exists(file_absolute_path):
        # Open the file and serve it as HttpResponse
        with open(file_absolute_path, 'rb') as file:
            response = HttpResponse(file.read(), content_type='application/pdf')  # Adjust the content type based on your file type
            response['Content-Disposition'] = f'inline; filename={os.path.basename(file_absolute_path)}'
            return response
    else:
        # Return a 404 response if the file doesn't exist
        return HttpResponse(status=404)