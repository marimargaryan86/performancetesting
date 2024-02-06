<script lang="ts">
  import StandardLayout from "~/components/page/standard-layout.svelte";
  import UserManuals from "./user-manuals.svelte";
  import Videos from "./videos.svelte";
  import Faq from "./faq.svelte";
  import { getPageTitle } from "~/utils/page-title";
  import { getTranslator } from "~/i18n";

  const t = getTranslator();
</script>

<svelte:head>
  <title>{getPageTitle($t("title"), $t("pages.knowledgeHub.title"))}</title>
</svelte:head>

<StandardLayout pageTitle={$t("pages.knowledgeHub.title")} backgroundImage="none">
  <div class="content">
    <UserManuals />

    <Videos />

    <Faq />
  </div>
</StandardLayout>

<style>
  .content {
    width: 100%;
    max-width: 1156px;
  }
</style>
