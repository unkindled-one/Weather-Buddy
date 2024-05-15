import database
import location
import userpreference

import numpy as np

testid = 271061629473521675

print("Going to set a zipcode and check if database updates it")
database.add_zip(str(testid), str(11111), "billydootest")

testcheck = database.get_zip(str(testid))

if '11111' == str(testcheck):
    print("Zipcode changed correctly")
else:
    print("Error zip code did not change")


print("Going to set a preference and check if the database updates it")
database.add_preference(str(testid), "10")

testcheck = database.get_preference(str(testid))

if testcheck == 10:
    print("Preference was added correctly")
else:
    print("ERROR: Preference was not added")

database.update_preference(str(testid), "5")

testcheck = database.get_preference(str(testid))

if testcheck == 5:
    print("Preference was updated correctly")
else:
    print("ERROR: Preference was not updated")

# zipcode checking

for zip_ in np.random.randint(0,99950,500,dtype=int): print(f'{zip_}: {location.valid_zipcode_check(zip_)}')
