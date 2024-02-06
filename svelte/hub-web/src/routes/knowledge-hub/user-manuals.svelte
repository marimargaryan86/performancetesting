<script lang="ts">
  import { getTranslator } from "~/i18n";
  import UserManualImage from "~/assets/images/user-manual.png";
  import Icon from "~/components/icons/icon.svelte";

  const t = getTranslator();

  const downloadUrl =
    "https://snowfall-public-files.s3.eu-north-1.amazonaws.com/junction/Junction+Hub+-+User+Manual+(ES).pdf";
</script>

<section>
  <h2 typography="headline-small" weight="bold">{$t("pages.knowledgeHub.userManuals.title")}</h2>
  <p typography="title-medium">
    {$t("pages.knowledgeHub.userManuals.description")}
  </p>

  <div class="download-manual">
    <a href={downloadUrl} target="_blank">
      <div class="download-title">
        <p typography="title-medium" weight="bold" color="var(--color-main-primary-900)">
          <Icon variant="pdf" color="var(--color-semantic-error-500)" />
          <span class="spacer" />
          {$t("pages.knowledgeHub.userManuals.userManual")}
        </p>
        <Icon variant="download" color="var(--color-main-primary-500)" />
      </div>
      <img src={UserManualImage} alt="user-manual" />
    </a>
  </div>
</section>

<style>
  .download-manual {
    width: 325px;
    margin: 16px 24px;
  }

  .download-title {
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
    padding: 16px 0;
  }

  section > p {
    color: var(--color-common-light-medium);
  }

  .download-title > p {
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
  }

  .spacer {
    margin-right: 8px;
  }

  section {
    display: flex;
    flex-flow: column;
    gap: 16px;
    margin-bottom: 48px;
    color: var(--color-common-light-strong);
  }

  a {
    color: var(--color-common-light-strong);
    text-decoration: none;
  }
</style>
