# Sentry

## Goal of Sentry

Our goal is to keep [Sentry][sentry] silent by fixing bugs or handling errors.

Whenever you have spare time, you can have a look in [Sentry][sentry] for a suitable issue. There are however some guidelines around this to help focus on the most important things.

## Guidelines

### Unhandled issues over handled issues

These are entirely unexpected and are missing error handling, so they are likely due to a bug, as opposed to the handled issues that are only reported because we catch exceptions and use the error or exception methods when logging.

### New issues over old issues

New issues are likely something that was caused by a recent commit, and Sentry usually even provides a likely cause. There is also information in Sentry about which version (commit hash) that the issue was first seen. Older issues have been around for a while and might not be mission critical to fix, because otherwise they would have been earlier.

### Frequent issues over infrequent issues

If something has happened just a few times it is likely not as urgent as something that is happening tens or hundreds of times. Look at a short recent timeline to see how urgent it is.


### Issues in critical systems over issues in non-critical system.

Some systems that are less mission critical are much less prioritized compared to the ones that are necessary for the core flow to work.

## Understanding the issue

There is also important to understand the issue before starting to work on it. Some things are due to errors in other systems, and that might end up not being something that we can fix on our end, but instead requiring us to raise an issue with a third party. Some issues might also need a product decision, especially when it comes to error handling of a third party system, because there might be some complex business logic that needs to be written to handle certain behaviors.

If an issue seems too strange or hard, either start a discussion in `#junction-backend-devs` about the issue or don't pick it.

## Working with Sentry

When finally starting to work on something, assign the issue to yourself to communicate to others that you are working on that particular issue.

Once your MR that should fix the issue is merged, remember to mark the issue as “Resolved in” the specific commit hash. If your issue was caused by something external, like a broken database or something else environment related, or perhaps by another service, then you can simply resolve it.

[sentry]: https://sentry.snowfall.se
