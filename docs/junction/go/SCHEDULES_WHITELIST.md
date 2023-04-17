---
internal: true
---

# Schedules Pipeline Whitelist

In the schedules pipeline there are a few methods we use to include schedules for
certain operators/agencies.

Any of these whitelists can be easily modified directly in Gitlab by clicking the edit
button.

- In the commit message field enter 'chore: update schedules whitelist'.
- Click the 'commit changes' button.
- This should then redirect to a 'New merge request' form.
- Leave all the fields as default and click the 'Create merge request' button.
- Someone will be automatically assigned to review the changes and it will then get merged.
- You can verify that it has been done when the 'Open' under the title changes to 'Merged'.

## SSIM (air)

The SSIM download has a whitelist of airlines (this allows us to skip processing
unwanted airlines in the import step).

The whitelist is in [airlines.json](/golang/cmd/ssim-convert/airlines.json).
Before adding new airlines to the file, ensure they are available in the download.

To find which airlines are available, but not currently being used, go to:
https://git.snowfall.se/junction/schedules/-/merge_requests/1
From the last CI run, open the 'oag' job.
Search the logs for 'SKIP carrier'.

## Distribusion (bus)

Distribusion also has a whitelist which allows us to skip downloading unused operators.

The whitelist is in the [code](/python/snowfall/project/junction/go/service/data_pipeline/distribusion_plugin.py).
Just add operators to `CARRIER_CODES`.

To see the available codes, go to:
https://git.snowfall.se/junction/schedules/-/merge_requests/1
From the last CI run, open the 'feeds' job.
Search the logs for 'Distribusion: Available codes'.

## All files

Once all files are downloaded, we can skip operators that are unused in the import step.

The whitelist for this is in [routes-whitelist.json](/golang/cmd/gtfs-import/routes-whitelist.json).
For each source file, `"types"` must be defined, which provides a list of schedules types
that should be imported.
Then, we can also add `"operators"` which must be a list of operators to include in the import.
If `"operators"` is not defined, then all operators will be included by default.
The operator names must be exact matches.

To find available operator names, go to:
https://git.snowfall.se/junction/schedules/-/merge_requests/1
From the last CI run, open the 'import' job.
Search the logs for 'Skip operator'.
