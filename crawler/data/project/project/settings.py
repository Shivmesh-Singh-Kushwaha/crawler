MONGODB = {
    'connection': {},
    'dbname': '{{ project_name }}',
}

try:
    from project.settings_local import *
except ImportError:
    pass
