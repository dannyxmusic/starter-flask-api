from gunicorn.app.wsgiapp import run
import subprocess
import sys

# Install dependencies from requirements.txt
subprocess.run(['pip', 'install', '-r', 'requirements.txt'], check=True)

# Import run from gunicorn

if __name__ == '__main__':
    # Start the server using gunicorn
    sys.argv = "gunicorn --bind 0.0.0.0:5151 app:app".split()
    sys.exit(run())
