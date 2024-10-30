import subprocess
import os

# Path to the file in the same directory as the script
file_path1 = os.path.join(os.path.dirname(__file__), 'parse.py')
file_path2 = os.path.join(os.path.dirname(__file__), 'extract.py')
file_path3 = os.path.join(os.path.dirname(__file__), 'compare.py')

subprocess.run(['python', file_path1])
subprocess.run(['python', file_path2])
subprocess.run(['python', file_path3])