<script lang="ts">
  import { invalidateAll } from "$app/navigation";
  import EmailIcon from "assets/icons/email-icon.svelte";
  import JunctionIcon from "assets/icons/junction-icon.svelte";
  import JunctionLogoDetailed from "assets/icons/junction-logo-detailed.svelte";
  import JunctionLogo from "assets/icons/junction-logo.svelte";
  import LockIcon from "assets/icons/lock-icon.svelte";
  import TextField from "components/ui/text-field.svelte";
  import integrationInstances from "integration-instances";

  let pending = false;
  let data = {
    email: "",
    password: "",
  };
  let errors: Partial<{
    email: string | boolean;
    password: string | boolean;
  }> = {};

  async function login(): Promise<void> {
    if (pending) {
      return;
    }

    pending = true;
    errors = {};

    try {
      const token = await integrationInstances.auth.createToken(data);

      document.cookie = `session-token=${token}; path=/; secure=true; samesite=none;`;

      await invalidateAll();
    } catch (error) {
      errors.email = true;
      errors.password = " Email/Username & Password not recognised. Please correct and try again";
    } finally {
      pending = false;
    }
  }

  function createClearErrorFunc(key: keyof typeof errors): () => void {
    return () => {
      errors[key] = undefined;
    };
  }
</script>

<main>
  <section class="left">
    <JunctionIcon />

    <div class="intro">
      <JunctionLogo />

      <span>Travel made</span>
      <strong>Simple</strong>
    </div>
  </section>

  <section class="right">
    <form on:submit|preventDefault={login} novalidate>
      <JunctionLogoDetailed />

      <h1 class="typography headline-small bold">
        <span>Log in</span>
        <hr />
      </h1>

      <TextField
        type="email"
        label="Email"
        placeholder="Enter your email"
        error={errors.email}
        bind:value={data.email}
        on:input={createClearErrorFunc("email")}
      >
        <EmailIcon slot="icon-before" />
      </TextField>

      <TextField
        type="password"
        label="Password"
        placeholder="Enter your password"
        error={errors.password}
        bind:value={data.password}
        on:input={createClearErrorFunc("password")}
      >
        <LockIcon slot="icon-before" />
      </TextField>

      <button class="primary large typography title-medium bold">Login</button>
    </form>
  </section>
</main>

<style>
  main {
    display: grid;
    grid-template-columns: 1fr 1fr;
    height: 100vh;
  }

  .left {
    display: flex;
    flex-flow: column;
    height: 100%;
    padding-left: 16px;
    background-image: url("/images/background.png");
    background-repeat: no-repeat;
    background-position: bottom left;
    background-size: cover;
  }

  .left > :global(svg) {
    margin: 16px 0;
  }

  .intro {
    align-self: flex-end;
    width: 100%;
    max-width: 631px;
    margin-top: 68px;
    padding: 282px 44px 54px;
    color: var(--color-neutral-800);
    background: rgb(255 255 255 / 0.4);
    border-radius: 20px 0 0 20px;
    backdrop-filter: var(--blur-large);
  }

  .intro > span {
    display: block;
    margin-top: 29.5px;
    font-weight: 400;
    font-size: 24px;
    font-family: "Red Hat Display", Arial, Helvetica, sans-serif;
    font-style: normal;
    line-height: 64px;
    letter-spacing: 4px;
    text-transform: uppercase;
  }

  .intro > strong {
    display: block;
    font-weight: 700;
    font-size: 96px;
    font-family: Raleway, Arial, Helvetica, sans-serif;
    font-style: normal;
    line-height: 64px;
  }

  form {
    display: flex;
    flex-flow: column;
    gap: 24px;
    align-items: flex-end;
    width: 100%;
    max-width: 656px;
    padding: 146px 16px;
  }

  form > :global(*) {
    width: 100%;
    max-width: 448px;
  }

  h1 {
    margin-top: 64px;
    color: var(--color-neutral-800);
  }

  hr {
    width: 37px;
    margin: 20px 0 4px;
    border: 0;
    border-top: var(--color-primary-500) 4px solid;
  }
</style>
