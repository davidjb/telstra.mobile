import time
import logging; logging.basicConfig(level=logging.DEBUG)
from telstra.mobile import autodetect_account

helper = autodetect_account('04123456890')
target = autodetect_account('04987654321')

# Send credit from target to the helper to start
target.creditme2u(helper.phone_number, 10)
time.sleep(15)

# Transfer all of it back again!
for i in range(8): 
    helper.creditme2u(target.phone_number, 1).reply('00').cancel()
    time.sleep(5)

print target.expiry_date
