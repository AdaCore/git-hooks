from git import git, get_object_type

print("DEBUG: Test the git --switch=False attribute")
print(git.log("-n1", pretty="format:%P", _decode=True).strip())

print("DEBUG: A Test to verify that git does not do any lstrip-ing...")
print(git.log("-n1", "space-subject", pretty="format:%s", _decode=True))

print("DEBUG: Unit test get_object_type with a null SHA1...")
print(get_object_type("0000000000000000000000000000000000000000"))
