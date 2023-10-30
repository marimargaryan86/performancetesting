<script lang="ts">
  import { formatAmount } from "formatting/currency";
  import type { OrderMarkupsModel } from "integration/junction-mobile-api/schemas/order";

  export let orderMarkups: OrderMarkupsModel;
</script>

<div class="fees">
  <div class="fees-breakdown">
    <ul>
      <li>
        <span class="typography label-medium">Service fee</span>
        <span class="typography body-small bold">
          {formatAmount({ ...orderMarkups.serviceFee }, undefined, true)}
        </span>
      </li>
      <li>
        <span class="typography label-medium">Agency mark-up</span>
        <span class="typography body-small bold">
          {formatAmount({ ...orderMarkups.agencyMarkup }, undefined, true)}
        </span>
      </li>
    </ul>
  </div>

  <div class="total">
    <span class="typography body-xlarge bold">Total to collect</span>
    <em class="typography body-xlarge bold total-amount">
      {formatAmount({ ...orderMarkups.totalToCollect }, undefined, true)}
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
