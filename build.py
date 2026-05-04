import subprocess

subprocess.run(['python', 'manage.py', 'migrate', '--run-syncdb'], check=True)
