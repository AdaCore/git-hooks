from config import git_config, UnsupportedOptionName

try:
    git_config("bad option name")
    print("*** Error: An exception should have been raised.")
except UnsupportedOptionName:
    print("+++ Exception raised as expected.")
