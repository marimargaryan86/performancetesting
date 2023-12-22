<script lang="ts">
  import { formatAmount } from "formatting/currency";
  import { getLocale, getLocaleData } from "i18n";
  import type { Markups } from "integration/junction-mobile-api/schemas/markups";

  export let markups: Markups;

  const locale = getLocale();
  const i18n = getLocaleData();
</script>

<div class="fees">
  <div class="fees-breakdown">
    <ul>
      <li>
        <span class="typography label-medium">{$i18n.words.serviceFee}</span>
        <span class="typography body-small bold">
          {formatAmount(markups.serviceFee, { locale: $locale, sign: true })}
        </span>
      </li>
      <li>
        <span class="typography label-medium">{$i18n.words.agencyMarkup}</span>
        <span class="typography body-small bold">
          {formatAmount(markups.agencyMarkup, { locale: $locale, sign: true })}
        </span>
      </li>
    </ul>
  </div>

  <div class="total">
    <span class="typography body-xlarge bold">{$i18n.sentences.totalToCollect}</span>
    <em class="typography body-xlarge bold total-amount">
      {formatAmount(markups.totalToCollect, { locale: $locale, sign: true })}
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
