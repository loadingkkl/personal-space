import subprocess
import os

subprocess.run(['python', 'manage.py', 'migrate', '--run-syncdb'], check=True)
if os.environ.get('ADMIN_USERNAME') and os.environ.get('ADMIN_PASSWORD'):
    subprocess.run(['python', 'manage.py', 'ensure_superuser'], check=True)
subprocess.run(['python', 'manage.py', 'collectstatic', '--noinput'], check=True)
