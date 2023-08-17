---
sidebar_position: 4
---

# Translations

Across our monorepo we are marking user-facing strings for translation.
Developers are expected to keep an eye out for strings that should be
translated in their own code and when reviewing PRs.

## Translating strings

Marking a string for translation is easy:

```python
from gettext import gettext as _
_("This string will be translated")
```

For plural cases:

```python
from gettext import ngettext as _n
_n("{n} thing", "{n} things", n).format(n=n)
```

:::warning

It is important that any string formatting is done _outside_ the translation
function (correct: `_("{0}").format(x)`, wrong: `_("{0}".format(x))`.

:::

## What is a user-facing string?

User-facing means that an end user will see the string, not a developer.
So, most exception or error messages on the API are not user-facing (unless
it's expected for the frontend to display the error message directly to the
user), as these will be mostly information for the developer during integration.

## Translating variables

The translation function must be used with string constants, not variables.
However, in rare cases, it is needed to translate variables dynamically.
For example, we can't simply use the translation function for a global constant,
otherwise everyone would just see the English translation (the translation
function must be called for each user request).

If you find yourself with this problem, please refer to the gettext
documentation for ways to make this work:
https://docs.python.org/3/library/gettext.html#deferred-translations

## Providing context to translators

Translators will only see the raw string without context, so in some cases
it is not clear what the meaning of the string is, in which case a comment
should be added with the `Translators:` prefix:

```python
# Translators: Marks emails as having been read.
button_label = _("Read")

# Translators: A manual process
title = _("Manual")
```

In the above examples, the comments will be extracted and shown to the
translator. Without these comments the translator may think the first
example is a present tense verb to read something or that the second
example refers to an instruction book.
