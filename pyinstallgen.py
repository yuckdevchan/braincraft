import os
import sys

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

assets_dir = 'assets/'
add_data_options = []

# Walk through the assets directory
for dirpath, dirnames, filenames in os.walk(assets_dir):
    # Generate the --add-data option for each file
    for filename in filenames:
        file_path = os.path.join(dirpath, filename)
        # Use the resource_path function to get the correct path
        correct_path = resource_path(file_path)
        add_data_options.append(f'--add-data "{correct_path};{correct_path}"')

# Join all the --add-data options into a single string
add_data_options_str = ' '.join(add_data_options)

# Print the PyInstaller command
print(f'pyinstaller main.py --noconsole --clean --onefile {add_data_options_str} --icon "assets/textures/icon.ico"')