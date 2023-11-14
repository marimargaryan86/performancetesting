<script lang="ts" context="module">
  const refundDataModel = z.object({
    us: z.number().min(0),
    reseller: z.number().min(0),
    externalReference: z.string().optional(),
  });

  type RefundData = z.infer<typeof refundDataModel>;
</script>

<script lang="ts">
  import LoadingIcon from "components/icons/loading-icon.svelte";
  import Button from "components/ui/button.svelte";
  import TextField from "components/ui/text-field.svelte";
  import integrationInstancesClient from "integration-instances-client";
  import type { TripBooking } from "integration/junction-hub-api/schemas/booking";
  import type { Transaction } from "integration/junction-hub-api/schemas/transaction";
  import { slideFade } from "transitions/slide-fade";
  import { pendableCall } from "utils/pendable-call";
  import { z } from "zod";

  export let transaction: Transaction;
  export let booking: TripBooking;

  let errors: z.ZodFormattedError<z.infer<typeof refundDataModel>> | undefined;
  let refundType: "with-amount" | "no-amount" = "no-amount";
  let refundPosition = booking.refund?.refundPosition;
  let refundData: RefundData = { us: 0, reseller: 0 };
  let refundDataDirty = true;

  $: if (refundType === "no-amount") {
    refundPosition = undefined;
    refundData = { us: 0, reseller: 0 };
  }

  $: refundData, (refundDataDirty = true);

  const { pending: refreshPending, func: refreshRefundPosition } = pendableCall(
    async (): Promise<void> => {
      if (!(booking.refund && refundDataDirty)) {
        return;
      }

      refundDataDirty = false;

      const parseResult = refundDataModel.safeParse(refundData);

      if (!parseResult.success) {
        return;
      }

      if (parseResult.data.reseller === 0 && parseResult.data.us === 0) {
        refundPosition = {
          amount: 0,
          currency: transaction.amounts.beneficiary.currency,
        };

        return;
      }

      refundPosition = (
        await integrationInstancesClient.hub.refunds.getRefundPosition({
          refundId: booking.refund.id,
          data: {
            refunded: {
              reseller: {
                currency: transaction.amounts.quotation.currency,
                amount: parseResult.data.reseller,
              },
              us: {
                currency: transaction.amounts.beneficiary.currency,
                amount: parseResult.data.us,
              },
            },
          },
        })
      ).total;
    },
  );

  const { pending, func: refund } = pendableCall(async () => {
    if (!(booking.refund && transaction.invoiceReference)) {
      return;
    }

    errors = undefined;

    const parseResult = refundDataModel.safeParse(refundData);

    if (!parseResult.success) {
      errors = parseResult.error.format();

      return;
    }

    if (
      parseResult.data.us === 0 &&
      parseResult.data.reseller === 0 &&
      !confirm("Are you sure you want to create a refund with no amounts?")
    ) {
      return;
    }

    booking.refund = await integrationInstancesClient.hub.refunds.update({
      id: booking.refund.id,
      data: {
        transactionId: transaction.id,
        invoiceReference: transaction.invoiceReference,
        externalReference: parseResult.data.externalReference,
        received: true,
        refunded: {
          reseller: {
            currency: transaction.amounts.quotation.currency,
            amount: parseResult.data.reseller,
          },
          us: {
            currency: transaction.amounts.beneficiary.currency,
            amount: parseResult.data.us,
          },
        },
        note: "",
      },
    });
  });
</script>

<div class="refund-dialog" transition:slideFade={{ duration: 300 }}>
  <h3 class="typography title-large bold">Refund</h3>

  <div class="refund-type typography body-medium">
    <label>
      <input type="radio" value="no-amount" bind:group={refundType} /> No amounts
    </label>
    <label>
      <input type="radio" value="with-amount" bind:group={refundType} /> With amounts
    </label>
  </div>

  {#if refundType === "no-amount"}
    <Button on:click={refund} variant="outline">Refund with no amount</Button>
  {:else}
    <form on:submit|preventDefault={refund}>
      <div>
        <TextField
          label="Provider - how much we get back"
          required
          type="number"
          placeholder="Amount"
          bind:value={refundData.us}
          error={errors?.us?._errors}
          step="any"
        >
          <span slot="icon-after" class="icon typography body-small currency">
            {transaction.amounts.beneficiary.currency}
          </span>
        </TextField>
      </div>

      <div>
        <TextField
          label="Reseller - how much we give back"
          required
          type="number"
          placeholder="Amount"
          bind:value={refundData.reseller}
          error={errors?.reseller?._errors}
          step="any"
        >
          <span slot="icon-after" class="icon typography body-small currency">
            {transaction.amounts.quotation.currency}
          </span>
        </TextField>
      </div>

      <div>
        <TextField
          label="Refund position"
          required
          readonly
          type="number"
          placeholder="Amount"
          value={refundPosition?.amount}
          step="any"
        >
          <span slot="icon-after" class="icon typography body-small currency">
            {refundPosition?.currency ?? transaction.amounts.beneficiary.currency}
          </span>
        </TextField>
      </div>

      {#if refundDataDirty || $refreshPending}
        <Button on:click={refreshRefundPosition}>
          Calculate refund position
          {#if $refreshPending}<LoadingIcon />{/if}
        </Button>
      {:else}
        <Button type="submit">
          Issue refund
          {#if $pending}<LoadingIcon />{/if}
        </Button>
      {/if}
    </form>
  {/if}
</div>

<style>
  .refund-dialog {
    display: flex;
    flex-flow: column;
    gap: 32px;
    padding: 32px 48px 48px;
    color: var(--color-main-primary-900);
    background-color: var(--color-common-background-light-main);
    border-radius: 16px;
  }

  .refund-type {
    display: flex;
    gap: 16px;
    align-items: center;
  }

  .refund-type > label {
    display: flex;
    gap: 4px;
    align-items: center;
  }

  .currency {
    display: flex;
    align-items: center;
    color: var(--color-common-light-soft);
  }

  form {
    display: flex;
    flex-flow: column;
    gap: 16px;
  }

  form > div > :global(.text-field) {
    --label-font-weight: 600;
    --label-font-family: "Inter";
    --label-font-size: 12px;
    --height: 46px;

    width: 100%;
  }
</style>
