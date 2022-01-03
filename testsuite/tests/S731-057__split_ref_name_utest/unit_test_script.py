from git import split_ref_name

namespace, short_name = split_ref_name("refs/funny")
print(namespace)
print(short_name)
