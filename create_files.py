import os

def create_file(file_path, content=''):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w') as f:
        f.write(content)

# Create __init__.py in api directory
create_file('api/__init__.py')

# Create apps.py in api directory
create_file('api/apps.py', """from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'
""")

print("Files created successfully!")
