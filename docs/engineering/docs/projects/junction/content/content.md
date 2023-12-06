# Content Providers

## Purpose

Content providers are where we get all the content from. How each
integration gathers information from the provider can be slightly
different case by case, as some flows are more intricate or granular than
others.

The main idea is to treat all providers as if they were third party code,
meaning we have to have a clearly defined interface between Junction Go and
the providers.

With the new provider integrations, we have tried to move a lot of the
responsibilities that was previously handled inside each integration to
Junction Go, hopefully simplifying writing new services.

## How it works

Each provider is a collection of different gRPC services, using interfaces
defined by Junction Go. The most central service is the `MetaService`,
providing information about the service and its current capabilities.
