# Setup
* See CONTRIBUTING.md for junction project setup with pants

# Usage
* Run locally with pants injecting parameters:

```
# junction $
pants test test.py \
--pytest-args='-m integration' \
-- \
--API-TOKEN=token \
--DEPARTURE_AFTER=date \
--ORIGIN=origin_uuid \
--DESTINATION=destination_uuid \
--HOST=hostname
```
Example command (substitute token)
```
# junction $
pants --force --output=all test python/snowfall/project/junction/api_automation/trip_test.py \
--pytest-args='-m integration' \
-- \
--API-TOKEN=token \
--DEPARTURE_AFTER=2022-08-27T00:00:00.000Z \
--ORIGIN=abc61467-7b1d-5b89-964b-3fc777fce304 \
--DESTINATION=53672c83-a75c-5263-a6df-4b9280bc363c \
--HOST=api.junction.dev
```
