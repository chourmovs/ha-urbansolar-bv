import os
import shutil

BASE_CONFIG_DIR = "/config"
COMPONENT_CONFIG_DIR = os.path.join(os.path.dirname(__file__), "config")

FILES_TO_COPY = ["input_numbers.yaml", "sensors.yaml", "utility_meters.yaml"]

def copy_yaml_files():
    for filename in FILES_TO_COPY:
        src_path = os.path.join(COMPONENT_CONFIG_DIR, filename)
        dest_path = os.path.join(BASE_CONFIG_DIR, filename)

        if not os.path.exists(dest_path):
            shutil.copyfile(src_path, dest_path)
        else:
            # Append the content if not already present (very naïve)
            with open(src_path, "r") as src, open(dest_path, "a") as dest:
                dest.write("\n\n# --- Added by urbansolar_battery ---\n")
                dest.write(src.read())
