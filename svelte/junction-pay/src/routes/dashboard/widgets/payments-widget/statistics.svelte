<script lang="ts">
  import type { Payment } from "$models/pay-models";
  import utils from "$lib/utils";
  import StatisticsColumn from "./statistics-column.svelte";

  export let payments: Payment[] = [];

  const currWeek = utils.setWeekStart(utils.setZeroTime(new Date()));
  const weekDates = [...Array(6)].map((_, idx) => {
    const week = new Date(currWeek);
    week.setDate(week.getDate() + (idx - 2) * 7);

    return week;
  });
  const paymentsGroupedByWeek: Payment[][] = [...Array(6)].map(() => []);

  payments.forEach((payment) => {
    const dueDate = utils.setZeroTime(new Date(payment.dueDate));

    if (dueDate < weekDates[1]) {
      paymentsGroupedByWeek[0].push(payment);
    } else if (dueDate < weekDates[2]) {
      paymentsGroupedByWeek[1].push(payment);
    } else if (dueDate < weekDates[3]) {
      paymentsGroupedByWeek[2].push(payment);
    } else if (dueDate < weekDates[4]) {
      paymentsGroupedByWeek[3].push(payment);
    } else if (dueDate < weekDates[5]) {
      paymentsGroupedByWeek[4].push(payment);
    } else {
      paymentsGroupedByWeek[5].push(payment);
    }
  });

  const busiestWeek = Math.max(...paymentsGroupedByWeek.map((paymentWeek) => paymentWeek.length));
  const dateFormat: Intl.DateTimeFormatOptions = { month: "short", day: "numeric" };
  const weeks = paymentsGroupedByWeek.map((paymentWeek, idx) => {
    const label: string =
      {
        0: "Older",
        2: "This week",
        5: "Future",
      }[idx] ??
      `${weekDates[idx].toLocaleDateString("en-US", dateFormat)} - ${(() => {
        const end = new Date(weekDates[idx]);
        end.setDate(end.getDate() + 6);

        return end.toLocaleDateString("en-US", dateFormat);
      })()}`;

    return {
      label,
      percentage: paymentWeek.length ? paymentWeek.length / busiestWeek : 0,
      sum: paymentWeek.reduce((prev, curr) => prev + curr.price.amount, 0),
      currency: paymentWeek[0]?.price.code,
    };
  });
</script>

<div class="statistics">
  {#each weeks as week}
    <StatisticsColumn {week} />
  {/each}
</div>

<style>
  .statistics {
    display: grid;
    font-size: 8px;
    grid-template-columns: repeat(6, calc(100% / 6));
    height: 176px;
  }
</style>
