import subprocess

subprocess.run(['python', 'manage.py', 'migrate', '--run-syncdb'], check=True)
subprocess.run(['python', 'manage.py', 'collectstatic', '--noinput'], check=True)
