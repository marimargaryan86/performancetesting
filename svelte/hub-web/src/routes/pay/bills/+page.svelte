<script lang="ts">
  import StandardLayout from "components/page/standard-layout.svelte";
  import Switch from "components/ui/switch.svelte";
  import Header from "components/ui/table/header.svelte";
  import TActionsCol from "components/ui/table/t-actions-col.svelte";
  import TBody from "components/ui/table/t-body.svelte";
  import TCol from "components/ui/table/t-col.svelte";
  import THead from "components/ui/table/t-head.svelte";
  import TRow from "components/ui/table/t-row.svelte";
  import Table from "components/ui/table/table.svelte";
  import { formatAmount } from "formatting/currency";

  const bills = [
    {
      orderId: "abc123",
      owedToUs: { amount: 123456, currency: "USD" },
      reconciled: true,
    },
    {
      orderId: "zxc936",
      owedToUs: { amount: 84234, currency: "USD" },
      reconciled: false,
    },
    {
      orderId: "qwe12039",
      owedToUs: { amount: 9812, currency: "USD" },
      reconciled: true,
    },
  ];
</script>

<StandardLayout pageTitle="Bills" searchQuery="">
  <Table>
    <THead>
      <Header>Order ID</Header>
      <Header>Owed to us</Header>
      <Header>Reconciled?</Header>
      <Header />
    </THead>
    <TBody>
      {#each bills as bill}
        <TRow>
          <TCol>{bill.orderId}</TCol>
          <TCol>
            <span class="money">
              <span>{formatAmount(bill.owedToUs)}</span>
              <em class="typography body-xsmall">{bill.owedToUs.currency}</em>
            </span>
          </TCol>
          <TCol class="reconciled">
            <Switch bind:active={bill.reconciled} />
          </TCol>
          <TActionsCol>
            <button class="action">
              <span>...</span>
            </button>
          </TActionsCol>
        </TRow>
      {/each}
    </TBody>
  </Table>
</StandardLayout>

<style>
  .action {
    padding: 4px;
    background-color: transparent;
    border: 0;
    transform: rotateZ(90deg);
    cursor: pointer;
  }

  .money {
    display: inline-flex;
    gap: 4px;
    align-items: center;
  }

  .money > em {
    color: var(--color-main-neutral-600);
  }

  :global(td.reconciled) {
    --width: 0;

    white-space: nowrap;
    text-align: right;
  }

  :global(td.reconciled .switch) {
    --width: 40px;
  }
</style>
