<script lang="ts">
  import { invalidateAll } from "$app/navigation";
  import EmailIcon from "components/icons/email-icon.svelte";
  import JunctionLogo from "components/icons/junction-logo.svelte";
  import LockIcon from "components/icons/lock-icon.svelte";
  import Button from "components/ui/button.svelte";
  import TextField from "components/ui/text-field.svelte";
  import integrationInstances from "integration-instances";

  let data = {
    email: "",
    password: "",
  };
  let errors: Partial<Record<keyof typeof data, string | boolean>> = {};
  let pending = false;

  async function login(): Promise<void> {
    if (pending) {
      return;
    }

    pending = true;

    try {
      const token = await integrationInstances.junctionPay.auth.createToken(data);
      const expiresAt = new Date();
      expiresAt.setMinutes(expiresAt.getMinutes() + 20);

      document.cookie = `session-token=${token}; expires=${expiresAt}; path=/;`;

      invalidateAll();
    } catch {
      errors = {
        email: true,
        password: "Email/Username & Password not recognised. Please correct and try again.",
      };
    } finally {
      pending = false;
    }
  }

  function clearErrors(): void {
    errors = {};
  }

  $: loginDisabled = data.email.trim().length < 3 || data.password.length < 6;
</script>

<svelte:head>
  <title>Login · Junction Hub</title>
</svelte:head>

<main>
  <JunctionLogo text={false} size={0.5} />

  <section class="intro">
    <JunctionLogo size={0.5} />

    <span>Travel payment made</span>
    <strong>Simple</strong>
  </section>

  <section class="login">
    <JunctionLogo snowfallTechnology poweredBy />

    <form on:submit|preventDefault={login} novalidate>
      <TextField
        label="Email"
        type="email"
        name="email"
        bind:value={data.email}
        error={errors.email}
        placeholder="Enter your email"
        on:input={clearErrors}
      >
        <EmailIcon slot="icon-before" color="var(--color-main-primary-500)" />
      </TextField>

      <TextField
        label="Password"
        type="password"
        name="password"
        bind:value={data.password}
        error={errors.password}
        placeholder="Enter your password"
        on:input={clearErrors}
      >
        <LockIcon slot="icon-before" color="var(--color-main-primary-500)" />
      </TextField>

      <Button type="submit" disabled={loginDisabled}>Login</Button>
    </form>
  </section>
</main>

<style>
  main {
    position: relative;
    display: grid;
    grid-template-columns: 1fr 1fr;
    align-items: center;
    width: 100%;
    height: 100vh;
    padding: 0 16px;
  }

  main > :global(.junction-logo) {
    position: absolute;
    top: 16px;
    left: 16px;
  }

  main::before,
  main::after {
    position: absolute;
    top: 0;
    left: 0;
    display: block;
    height: 100%;
    content: "";
  }

  main::before {
    z-index: -2;
    width: 100%;
    background-color: var(--color-common-dark-strong);
  }

  main::after {
    z-index: -1;
    width: 50%;
    background-image: url("/images/login-bg.png");
    background-repeat: no-repeat;
    background-size: cover;
  }

  .intro {
    display: flex;
    flex-flow: column;
    justify-content: flex-end;
    justify-self: flex-end;
    width: 100%;
    max-width: 631px;
    height: 100%;
    max-height: 563px;
    padding: 54px 44px;
    color: var(--color-main-neutral-800);
    background: rgb(255 255 255 / 0.4);
    border-radius: 20px 0 0 20px;
    backdrop-filter: blur(12px);
  }

  .intro > span {
    margin: 54px 0 12px;
    font-weight: 400;
    font-size: 24px;
    font-family: "Red Hat Display", Arial, Helvetica, sans-serif;
    font-style: normal;
    letter-spacing: 4px;
    text-transform: uppercase;
  }

  .intro > strong {
    font-weight: 700;
    font-size: 96px;
    font-family: Raleway, Arial, Helvetica, sans-serif;
    font-style: normal;
  }

  .login > :global(svg) {
    margin-bottom: 60px;
  }

  .login {
    display: flex;
    flex-flow: column;
    gap: 28px;
    align-items: center;
    width: 100%;
    max-width: 768px;
    padding-left: 16px;
  }

  form {
    display: inline-flex;
    flex-flow: column;
    gap: 24px;
    width: 100%;
    max-width: 448px;
  }
</style>
