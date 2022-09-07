<script lang="ts">
  import type { Payment } from "$models/pay-models";
  import routeConfig from "$lib/route-config";
  import { faker } from "@faker-js/faker";
  import WidgetHeader from "../widget-header.svelte";
  import Statistics from "./statistics.svelte";

  const minDate = new Date();
  minDate.setDate(minDate.getDate() - 21);
  const maxDate = new Date();
  maxDate.setDate(maxDate.getDate() + 28);

  const payments: Payment[] = [...Array(faker.datatype.number({ min: 0, max: 100 }))].map(() => ({
    price: {
      amount: faker.datatype.number({ min: 100, max: 400 }),
      code: "GBP",
    },
    dueDate: faker.date.between(minDate, maxDate),
  }));
</script>

<div class="payments-widget">
  <WidgetHeader viewMoreUrl={routeConfig.pay}>Pay</WidgetHeader>

  <h3>Invoices to be paid</h3>

  <div class="invoices">
    <strong>{payments.length} awaiting payments</strong>

    <Statistics {payments} />
  </div>
</div>

<style>
  h3 {
    align-items: center;
    background-color: rgb(255 255 255 / 20%);
    border: var(--color-white) 1px solid;
    border-radius: 10px;
    box-shadow: 0 -11px 37px rgb(0 0 0 / 3%);
    display: flex;
    height: 45px;
    margin-bottom: 12px;
    padding: 0 20px;
  }

  .invoices {
    background-color: var(--color-white);
    border-radius: 10px;
    box-shadow: 0 -11.6375px 37.3625px rgb(0 0 0 / 3%);
    padding: 25px 20px 20px;
  }

  strong {
    border-bottom: var(--color-gray-lightest) 1px solid;
    display: block;
    font-size: 14px;
    margin-bottom: 8px;
    padding: 0 0 16px;
  }
</style>
