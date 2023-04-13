import yaml
import os
def app_config():
    #### load configurations ####
    # Get the absolute path of the grandparent directory (3 layers up)
    rootdir = os.path.abspath(os.path.join(os.getcwd(), "../.."))
    # Load the file from the grandparent directory
    file_path = os.path.join(rootdir, "config.yaml")
    with open(file_path, "r") as file:
        # Read the contents of the file
        config = yaml.safe_load(file)
    return config