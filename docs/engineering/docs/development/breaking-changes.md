# Breaking Changes

:::danger

When adding, changing or removing functionality in a server application, don't
adapt your clients to that change in the same commit or merge request. If only the
client or the server ends up being deployed, the communication between the two
could be completely broken until everything is eventually successfully deployed.

Changes made in one commit or merge request are not guaranteed to be deployed
simultaneously or together (or at all) for various reasons (the deploy job could
fail, the server could have a multi-instance rollout strategy that spans several
hours, etc.).

:::

_To be written._
