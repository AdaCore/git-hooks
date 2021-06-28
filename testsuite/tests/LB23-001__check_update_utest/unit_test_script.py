from update import check_update
from utils import InvalidUpdate

try:
    check_update(
        "some/dummy_refname",
        "8ef2d60c830f70e70268ce886209805f5010db1f",
        "d065089ff184d97934c010ccd0e7e8ed94cb7165",
    )
    print("*** ERROR: Call to check_update did not raise an exception")
except InvalidUpdate as e:
    print("\n".join(e.args))
