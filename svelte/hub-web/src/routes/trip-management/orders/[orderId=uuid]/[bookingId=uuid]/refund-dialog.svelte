<script lang="ts" context="module">
  const refundDataModel = z.object({
    provider: z.object({
      currency: z.string(),
      amount: z.number().min(0),
    }),
    reseller: z.object({
      currency: z.string(),
      amount: z.number().min(0),
    }),
  });

  function formatCurrencyOption(currency?: Currency): string | undefined {
    return currency?.code;
  }

  function findCurrencyOption(query: string, option?: Currency): boolean {
    const queryLower = query.toLowerCase();

    return Boolean(
      option?.code.toLowerCase().includes(queryLower) ||
        option?.name.toLowerCase().includes(queryLower),
    );
  }
</script>

<script lang="ts">
  import LoadingIcon from "components/icons/loading-icon.svelte";
  import Button from "components/ui/button.svelte";
  import SelectField from "components/ui/select-field.svelte";
  import TextField from "components/ui/text-field.svelte";
  import integrationInstancesClient from "integration-instances-client";
  import type { TripBooking } from "integration/junction-hub-api/schemas/booking";
  import type { Currency } from "integration/junction-hub-api/schemas/currency";
  import type { Transaction } from "integration/junction-hub-api/schemas/transaction";
  import { slideFade } from "transitions/slide-fade";
  import { pendableCall } from "utils/pendable-call";
  import { z } from "zod";

  let currencyMap: Map<string, Currency>;
  export { currencyMap as currencies };
  export let transaction: Transaction;
  export let booking: TripBooking;

  let errors: z.ZodFormattedError<z.infer<typeof refundDataModel>> | undefined;

  let refundData: {
    provider: { currency?: Currency; amount?: number };
    reseller: { currency?: Currency; amount?: number };
  } = {
    provider: {},
    reseller: {},
  };

  $: currencies = Array.from(currencyMap.values());

  const { pending, func: refund } = pendableCall(async () => {
    errors = undefined;

    const parseResult = refundDataModel.safeParse({
      provider: {
        currency: refundData.provider.currency?.code,
        amount: refundData.provider.amount,
      },
      reseller: {
        currency: refundData.reseller.currency?.code,
        amount: refundData.reseller.amount,
      },
    });

    if (!parseResult.success) {
      errors = parseResult.error.format();

      return;
    }

    if (!transaction.invoiceReference) {
      return;
    }

    booking.refund = await integrationInstancesClient.hub.refunds.create({
      data: {
        transactionId: transaction.id,
        invoiceReference: transaction.invoiceReference,
        received: true,
        refunded: {
          reseller: parseResult.data.reseller,
          us: parseResult.data.provider,
        },
        note: "",
      },
    });
  });
</script>

<div class="refund-dialog" transition:slideFade={{ duration: 300 }}>
  <h3 class="typography title-large bold">Refund</h3>

  <form on:submit|preventDefault={refund}>
    <div>
      <TextField
        label="Provider - how much we get back"
        required
        type="number"
        placeholder="Amount"
        bind:value={refundData.provider.amount}
        error={errors?.provider?.amount?._errors}
      />
      <SelectField
        label="&nbsp;"
        search={findCurrencyOption}
        formatter={formatCurrencyOption}
        placeholder="Currency"
        options={currencies}
        bind:value={refundData.provider.currency}
        error={errors?.provider?.currency?._errors}
      />
    </div>

    <div>
      <TextField
        label="Reseller - how much we give back"
        required
        type="number"
        placeholder="Amount"
        bind:value={refundData.reseller.amount}
        error={errors?.reseller?.amount?._errors}
      />
      <SelectField
        label="&nbsp;"
        search={findCurrencyOption}
        formatter={formatCurrencyOption}
        placeholder="Currency"
        options={currencies}
        bind:value={refundData.reseller.currency}
        error={errors?.reseller?.currency?._errors}
      />
    </div>

    <Button type="submit">
      Go
      {#if $pending}<LoadingIcon />{/if}
    </Button>
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

  form {
    display: flex;
    flex-flow: column;
    gap: 16px;
  }

  form > div {
    display: grid;
    grid-template-columns: 1fr 130px;
    gap: 4px;
  }

  form > div > :global(.text-field),
  form > div > :global(.select-field) {
    --label-font-weight: 600;
    --label-font-family: "Inter";
    --label-font-size: 12px;
    --height: 46px;
  }
</style>
