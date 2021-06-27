from shutil import rmtree
import os

# Modules provided by git-hooks
import utils

assert utils.scratch_dir is None

print("DEBUG: Calling utils.create_scratch_dir (call #1)...")
utils.create_scratch_dir()

print("DEBUG: Deleting scratch dir...")
rmtree(utils.scratch_dir)

print("DEBUG: Calling utils.create_scratch_dir (call #2)...")
print("       (this call is expected to generate a warning)")
utils.create_scratch_dir()

print("DEBUG: Deleting crash dir again...")
rmtree(utils.scratch_dir)
