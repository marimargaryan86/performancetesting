<script lang="ts">
  import { formatAmount } from "$lib/formatting/currency";
  import { getLocale, getTranslator } from "~/i18n";
  import type { Markups } from "~/integration/junction-mobile-api/schemas/markups";

  export let markups: Markups;

  const locale = getLocale();
  const t = getTranslator();
</script>

<div class="fees">
  <div class="fees-breakdown">
    <ul>
      <li>
        <span typography="label-medium">{$t("words.serviceFee")}</span>
        <span typography="body-small" weight="bold">
          {formatAmount(markups.serviceFee, $locale, { sign: true })}
        </span>
      </li>
      <li>
        <span typography="label-medium">{$t("words.agencyMarkup")}</span>
        <span typography="body-small" weight="bold">
          {formatAmount(markups.agencyMarkup, $locale, { sign: true })}
        </span>
      </li>
    </ul>
  </div>

  <div class="total">
    <span typography="body-xlarge" weight="bold">{$t("sentences.totalToCollect")}</span>
    <em typography="body-xlarge" weight="bold" class="total-amount">
      {formatAmount(markups.totalToCollect, $locale, { sign: true })}
    </em>
  </div>
</div>

<style>
  .fees {
    margin: 0 -16px;
    padding: 16px;
  }

  .fees-breakdown {
    display: flex;
    flex-flow: column;
    gap: 8px;
  }

  .fees-breakdown > ul {
    display: flex;
    flex-direction: column;
    gap: 4px;
    padding: 0 0 16px;
  }

  .fees-breakdown > ul > li {
    display: flex;
    justify-content: space-between;
  }

  .total {
    display: flex;
    justify-content: space-between;
  }

  .total-amount {
    color: var(--color-main-primary-500);
  }
</style>
