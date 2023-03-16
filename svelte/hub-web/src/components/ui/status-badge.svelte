<script lang="ts">
  import { formatTransactionStatus } from "formatting/transaction";
  import type { TransactionStatus } from "models/transaction";

  export let value: TransactionStatus;
</script>

<span
  class="status-badge"
  class:paid={value === "paid"}
  class:cancelled={value === "cancelled"}
  class:pending={value === "pending"}
>
  {formatTransactionStatus(value)}
</span>

<style>
  .status-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 6px 12px;
    color: var(--color-generic-white);
    font-weight: 600;
    font-size: 8px;
    font-family: Poppins, Arial, Helvetica, sans-serif;
    font-style: normal;
    line-height: 12px;
    letter-spacing: 0.15px;
    border: 1px solid #d8dadd;
    border-radius: 8px;
  }

  .paid {
    background-image: radial-gradient(
      157.78% 1163.56% at -3.9% -43.33%,
      #4ccaab 0%,
      #2c9e83 34.38%,
      #3f8574 68.75%,
      #21735f 100%
    );
  }

  .cancelled {
    background-image: linear-gradient(121.87deg, #ff7777 -10.54%, #a2416b 98.97%);
  }

  .pending {
    background-image: linear-gradient(
      131.08deg,
      #f5dd00 -60.91%,
      #44dafb 143.29%,
      rgb(125 248 76 / 0.9245) 143.31%
    );
  }
</style>
