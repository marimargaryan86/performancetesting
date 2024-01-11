<script lang="ts" context="module">
  function getPassengerLabel(
    passenger: OrderPassenger,
    createdAt: Date,
    locale: LocaleData,
  ): string {
    const age = getAge(passenger.birthDate, createdAt);

    const def = Object.values(PASSENGER_DEFINITIONS).find((item) => {
      if (item.span.from <= age) {
        return age <= (item.span.to ?? Number.MAX_SAFE_INTEGER);
      }

      return false;
    });

    return def ? getPassengerFullLabel(def, locale) : locale.words.unknown;
  }
</script>

<script lang="ts">
  import type { OrderPassenger } from "integration/junction-mobile-api/schemas/order";
  import { getAge } from "utils/date-time";
  import {
    PASSENGER_DEFINITIONS,
    getPassengerFullLabel,
  } from "./trip-search/passenger-picker/passenger-picker.svelte";
  import { getLocaleData, type LocaleData } from "i18n";
  import Icon from "components/icons/icon.svelte";

  export let passengers: OrderPassenger[];
  export let orderCreatedAt: Date = new Date();

  const i18n = getLocaleData();
</script>

<ul class="passengers">
  <li class="typography body-large bold">{$i18n.words.passengerDetails}</li>
  {#each passengers as passenger}
    <li class="passenger typography body-large">
      <span class="circle">
        <Icon variant="passenger" size="20px" color="var(--color-main-primary-600" />
      </span>
      <strong class="typography bold">{passenger.firstName} {passenger.lastName}</strong>
      <em>{getPassengerLabel(passenger, orderCreatedAt, $i18n)}</em>
    </li>
  {/each}
</ul>

<style>
  .passengers {
    display: flex;
    flex-flow: column;
    gap: 16px;
  }

  .passenger {
    display: flex;
    gap: 8px;
    align-items: center;
    padding: 16px;
    border: var(--color-main-neutral-100) 1px solid;
    border-radius: 6px;
  }

  em {
    color: var(--color-main-neutral-600);
  }

  .circle {
    display: flex;
    flex-shrink: 0;
    align-items: center;
    justify-content: center;
    width: 40px;
    height: 40px;
    border: var(--color-main-primary-600) 1px solid;
    border-radius: 50%;
  }
</style>
