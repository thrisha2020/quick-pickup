import os

def setup_project_structure():
    # Create API directory and __init__.py
    api_dir = os.path.join('api')
    os.makedirs(api_dir, exist_ok=True)
    
    # Create __init__.py
    init_file = os.path.join(api_dir, '__init__.py')
    if not os.path.exists(init_file):
        with open(init_file, 'w') as f:
            f.write('')
    
    # Create apps.py
    apps_file = os.path.join(api_dir, 'apps.py')
    if not os.path.exists(apps_file):
        with open(apps_file, 'w') as f:
            f.write('''from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'
''')
    
    print("Project structure set up successfully!")

if __name__ == "__main__":
    setup_project_structure()
