<script lang="ts" context="module">
  const refundDataModel = z.discriminatedUnion("type", [
    z.object({
      type: z.literal("automatic"),
      externalReference: z.string().trim().min(1).optional(),
      us: z.number().min(0),
      reseller: z.number().min(0),
    }),
    z.object({
      type: z.literal("manual"),
      externalReference: z.string().trim().min(1),
      us: z.number().min(0).optional(),
      reseller: z.number().min(0).optional(),
    }),
  ]);

  type RefundData = z.infer<typeof refundDataModel>;

  function getRefundPutData(data: RefundData, transaction: Transaction): RefundPut {
    return data.type === "automatic"
      ? {
          type: "automatic",
          transactionId: transaction.id,
          invoiceReference: transaction.invoiceReference ?? "",
          externalReference: data.externalReference,
          received: true,
          refunded: {
            reseller: {
              currency: transaction.amounts.quotation.currency,
              amount: data.reseller ?? 0,
            },
            us: {
              currency: transaction.amounts.beneficiary.currency,
              amount: data.us ?? 0,
            },
          },
          note: "",
        }
      : {
          type: "manual",
          externalReference: data.externalReference,
        };
  }
</script>

<script lang="ts">
  import LoadingIcon from "components/icons/loading-icon.svelte";
  import Button from "components/ui/button.svelte";
  import TextField from "components/ui/text-field.svelte";
  import integrationInstancesClient from "integration-instances-client";
  import type { TripBooking } from "integration/junction-hub-api/schemas/booking";
  import type { Refund, RefundPut } from "integration/junction-hub-api/schemas/refund";
  import type { Transaction } from "integration/junction-hub-api/schemas/transaction";
  import { writable } from "svelte/store";
  import { slideFade } from "transitions/slide-fade";
  import { z } from "zod";

  export let transaction: Transaction;
  export let booking: TripBooking;

  let errors: z.ZodFormattedError<z.infer<typeof refundDataModel>> | undefined;
  let refundType: "with-amount" | "no-amount" = "no-amount";
  let refundData = getDefaultRefundData(booking.refund);
  let refundPosition = booking.refund?.refundPosition;
  let refundDataDirty = true;

  const refreshPending = writable(false);
  const refundPending = writable(false);

  $: if (refundType === "no-amount") {
    refundPosition = booking.refund?.refundPosition;
    refundData = getDefaultRefundData(booking.refund);
  }
  $: refundData, (refundDataDirty = refundData.type === "automatic");

  function getDefaultRefundData(refund?: Refund): RefundData {
    return refund?.status === "failed"
      ? { type: "manual", externalReference: "" }
      : {
          type: "automatic",
          us: refund?.refunded.us?.amount ?? 0,
          reseller: refund?.refunded.reseller?.amount ?? 0,
        };
  }

  async function refreshRefundPosition(): Promise<void> {
    if ($refreshPending) {
      return;
    }

    try {
      $refreshPending = true;

      if (!(booking.refund && refundDataDirty)) {
        return;
      }

      refundDataDirty = false;

      const parseResult = refundDataModel.safeParse(refundData);

      if (!parseResult.success) {
        return;
      }

      if (parseResult.data.type === "manual") {
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
    } finally {
      $refreshPending = false;
    }
  }

  async function performRefund(): Promise<void> {
    if ($refundPending) {
      return;
    }

    try {
      $refundPending = true;
      errors = undefined;

      if (!booking.refund) {
        return;
      }

      const parseResult = refundDataModel.safeParse(refundData);

      if (!parseResult.success) {
        errors = parseResult.error.format();

        return;
      }

      if (
        parseResult.data.type === "automatic" &&
        parseResult.data.us === 0 &&
        parseResult.data.reseller === 0 &&
        !confirm("Are you sure you want to create a refund with no amounts?")
      ) {
        return;
      }

      booking.refund = await integrationInstancesClient.hub.refunds.update({
        id: booking.refund.id,
        data: getRefundPutData(parseResult.data, transaction),
      });

      refundData = getDefaultRefundData(booking.refund);
    } finally {
      $refundPending = false;
    }
  }
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

  <form on:submit|preventDefault={performRefund}>
    {#if refundType === "with-amount"}
      <div>
        <TextField
          label="Provider - how much we get back"
          required={refundData.type === "automatic"}
          readonly={refundData.type === "manual"}
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
          required={refundData.type === "automatic"}
          readonly={refundData.type === "manual"}
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
          required={refundData.type === "automatic"}
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
    {/if}

    {#if refundData.type === "manual"}
      <div transition:slideFade={{ duration: 300 }}>
        <TextField
          label="Refund reference"
          required
          placeholder="Enter refund reference"
          bind:value={refundData.externalReference}
          error={errors?.externalReference?._errors}
          helpText="The refund has to be handled manually, please do so and enter the refund reference above"
        />
      </div>
    {/if}

    {#if refundType === "no-amount"}
      <Button type="submit" variant="outline">
        Refund with no amount
        {#if $refundPending}<LoadingIcon />{/if}
      </Button>
    {:else if refundDataDirty || $refreshPending}
      <Button on:click={refreshRefundPosition}>
        Calculate refund position
        {#if $refreshPending}<LoadingIcon />{/if}
      </Button>
    {:else}
      <Button type="submit">
        Issue refund
        {#if $refundPending}<LoadingIcon />{/if}
      </Button>
    {/if}
  </form>
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

  form > div {
    display: flex;
    flex-flow: column;
    gap: 8px;
  }

  form > div > :global(.text-field) {
    --label-font-weight: 600;
    --label-font-family: "Inter";
    --label-font-size: 12px;
    --height: 46px;

    width: 100%;
  }
</style>
