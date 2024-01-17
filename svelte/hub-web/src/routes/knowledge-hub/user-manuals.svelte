<script lang="ts">
  import { getLocaleData } from "i18n";
  import UserManualImage from "assets/images/user-manual.png";
  import Icon from "components/icons/icon.svelte";

  const i18n = getLocaleData();

  const downloadUrl = `https://file.notion.so/f/f/5b14a1b1-b088-42e9-a68f-d2dd3d227cf1/042cc0ea-3223-4bff-a022-8715b8e1ff53/Untitled.pdf?id=d08ceb41-73ce-47b7-a338-f1aafb85ba2e&table=block&spaceId=5b14a1b1-b088-42e9-a68f-d2dd3d227cf1&expirationTimestamp=1705406400000&signature=xuI6Wi0S1GTndZ4l2GBTnQn19k3HpmSRg2lZWCssFC8&downloadName=Untitled.pdf`;
</script>

<section>
  <h2 typography="headline-small" weight="bold">{$i18n.pages.knowledgeHub.userManuals.title}</h2>
  <p typography="title-medium">
    {$i18n.pages.knowledgeHub.userManuals.description}
  </p>

  <div class="download-manual">
    <a href={downloadUrl} target="_blank">
      <div class="download-title">
        <p typography="title-medium" weight="bold" color="var(--color-main-primary-900)">
          <Icon variant="pdf" color="var(--color-semantic-error-500)" />
          <span class="spacer" />
          {$i18n.pages.knowledgeHub.userManuals.userManual}
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
