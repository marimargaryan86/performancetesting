# Day One

Day One should be a case of you getting the appropriate log-ins and access to
systems you'll be using, you'll also be installing most of the tooling we use
too.

Once you've gone through this page and the directly linked pages, make yourself
familiar with the rest of these docs. Some pages are in-progress, if you have
additions you think would be useful, please make them!

## Say Hi :wave:

Stick a hello in [`#the-lounge`](https://snowfall.slack.com/archives/C09LX8UUC)
and introduce yourself! Cute pet pics more than welcome :cat: :dog:

You'll also want to make sure you've set up a profile photo in Slack and have
your name pronunciation and location filled out!

## General stuff

The following tasks are a bit HR-y but are needed to complete your onboarding,
a few are marked up as UK only, if you're not employed in the UK, don't do them!

### Personio

You'll have been given access to [Personio](https://snowfall.personio.de/),
please go to `My Profile` on the left and fill out all the fields
within `Personal Info`.

### Email Signature

Please take the following linked signature [template][Email Signature], open it
up in a text editor and replace the following:

```shell
{{{NAME}}} - Your first name and last name
{{{JOB_TITLE}}} - Your job title
{{{PHONE}}} - Your phone number incl international code - for example (+441234567890)
{{{EMAIL_PRE}}} - Email prefix (first part of your email before @snowfalltravel.com)
```

Then, depending on your email client, set this as your email signature. Please
send out an email from your work account to your personal account to check this
worked!

### HMRC Form & P45 (UK ONLY 🇬🇧)

If you're in the UK, please fill out [this][HMRC Form] form and send it along
with
your P45 to [`@Jackie`][Jackie] on Slack!

### Vitality Health Insurance (UK ONLY 🇬🇧)

If you're in the UK, you have the option to sign up to our private health
insurance
through [Vitality](https://www.vitality.co.uk/), if you're interested, reach out
to [`@Jackie`][Jackie] on Slack!

## Technical Setup

### Basic access

You will need access to a few things, most systems can be logged into with your
Snowfall Google account.

Please ensure you have access to:

* [Gitlab](https://git.snowfall.se/junction) - Code and task management
* [Sentry](https://sentry.snowfall.se) - Error management
* [Grafana](https://grafana.snowfall.se/) - Logs and metrics
* [Nomad Dev](https://nomad.junction.dev/) - Dev cluster (ask SRE for access)
* [Consul Dev](https://consul.junction.dev/) - Service directory (ask SRE for access)
* Junction VPN (If you're reading this, you already have this!)

### Understand Snowfall Development Practices

Before jumping in, take some time to understand the [development practices](/docs/development/) we
have established at Snowfall. In particular, skim through the following to get the right context:

1. We use a [Monorepo](https://en.wikipedia.org/wiki/Monorepo), except for a few projects (notably Junction One).
2. We use [trunk-based development](https://trunkbaseddevelopment.com/).
3. We use [conventional
commits](https://www.conventionalcommits.org/en/v1.0.0/) and have
standardized on some [Git
Etiquette](https://drive.google.com/drive/folders/1i5BdD4Ut76jee5kslsaeMaxDSzHAQzuc).
4. On each Merge Request (MR), we enforce several style rules with our
[CI/CD](/docs/development/ci-cd) and we require at least one approval.

### Junction GO/HUB/PAY/PLUS setup

Please refer to the steps in [Monorepo](/docs/monorepo/getting-started) as these
will outline how to install the necessary tools required for development
within GO/HUB/PAY/PLUS.

### Junction ONE setup

:::info

To be written

:::

## Get to know your Product Leads, Product Managers, Delivery Leads, and Lead Engineers

We're here to build amazing products with amazing people; your Product Leads,
Product Managers,
Delivery Leads, and Lead Engineers are here to help make sure yourself and your
fellow engineers are building important things that matter.

### Products and Product Leads

| Product  | Product Lead        |
|----------|---------------------|
| GO       | @pascal.b           |
| PAY      | @alexander.h        |
| HUB      | @Nick Castrioty     |
| PLUS     | @Natalia Vittoratou |
| SUPERAPP | @Harut Arakelyan    |
| ONE      | @Kevin Drury        |

### Our Squads and their Product Managers, Delivery Leads, and Lead Engineers

| Squad        | Product Manager     | Delivery Lead | Lead Engineer |
|--------------|---------------------|---------------|---------------|
| Squad 1      | @alexander.h        | @Soichi       | @Vagho        |
| Squad 2      | @Jorge Velasco      | @Beena        | @aram         |
| Squad 3      | @Phil               | @Josh         | @reuben       |
| Squad 4      | @Nick Castrioty     | @Josh         | @justin.k     |
| Squad 5      | @Natalia Vittoratou | @Beena        | @Nikos        |
| Squad 6      | @Harut Arakelyan    | @Soichi       | -             |
| Junction One | @Kevin Drury        | @Sam          | -             |

## Knowledge Fest 🤘

Knowledge Fest is an initiative to present and inform everyone at Snowfall about
different things we build, how we build them, and why.

You can find a link to all the current recordings
[here](https://www.notion.so/Knowledge-Fest-89b12f4c7ac645a18bb41f481f3e272c?pvs=4)

In particular, there is an old but still very relevant [Junction tech overview
series](https://www.notion.so/Junction-Videos-Tech-overview-deep-dives-e5e20703f1864a32bd8bd78b8eb97ee4)
of recordings (several hours), that gives a lot of context on how we build
software at Snowfall. We recommend that you watch this series at your own pace,
over the coming few weeks. Just keep in mind this was recorded in 2022 and not
everything is fully up-to-date.

[Email Signature]:https://www.notion.so/Email-Signature-Setup-June-2022-d8e677f963814c51b3c34a0b2dd9f274#5c5447c54f3c491e8a695ff59734a307

[HMRC Form]: https://file.notion.so/f/s/efafb1ec-dec6-45bc-875d-15188c236cc8/New_starter_form_.pdf?id=ae2ef22d-c81e-4539-b842-cfaeb3e58387&table=block&spaceId=5b14a1b1-b088-42e9-a68f-d2dd3d227cf1&expirationTimestamp=1696723200000&signature=vCFCWJu7syHW8XNazW6nXKPCtBz1YZXeR8mgEVhVfb8&downloadName=New+starter+form+.pdf

[Jackie]: https://snowfall.slack.com/team/U04M3C5GBJ6
