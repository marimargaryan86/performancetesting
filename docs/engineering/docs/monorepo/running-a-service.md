---
sidebar_position: 5

---

# Running a service

Now that you have your environment set up and junction cloned, let's try running a service manually.

It's generally favorable to run services through Pants (either in your IDE or terminal of choice) to get a more production-like experience, but running them through Python by exporting a virtual environment from Pants is also possible.

Regardless of method, you need to run `docker compose up` to boot up all required third-party services. Also remember that some first-party services have dependencies on other first-party services.

### Command Line

#### Pants

```shell
bash/run.sh python/snowfall/project/{project}/{subproject}/service/{service}/main.py {task}
```

:::info
Ensure you have the correct `bash` version installed (4.0+).
:::

