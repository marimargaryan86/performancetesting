<script lang="ts" context="module">
  export type BookingSearchData = {
    adults: number;
    children: number;
    infants: number;
    origin: string;
    destination: string;
    outbound: Date;
    inbound?: Date;
  };
</script>

<script lang="ts">
  import SearchIcon from "components/icons/book-search-icon.svelte";
  import DatePicker from "components/ui/date-picker/date-picker.svelte";
  import PassengerPicker from "./passenger-picker/passenger-picker.svelte";
  import routeConfig from "routeConfig";
  import { goto } from "$app/navigation";
  import Button from "components/ui/button.svelte";
  import TextField from "components/ui/text-field.svelte";
  import { page } from "$app/stores";

  export let firstStep = true;

  export let data: Partial<BookingSearchData> = {
    origin: "",
    destination: "",
    outbound: undefined,
    adults: 0,
    children: 0,
    infants: 0,
  };

  function getSearchQuery(nextData: Partial<BookingSearchData>): URL {
    if (!formValid(nextData)) {
      throw new Error("Invalid search data");
    }

    const url = new URL(routeConfig.book.select.root, $page.url.href);

    url.searchParams.set("origin", nextData.origin);
    url.searchParams.set("destination", nextData.destination);

    if (nextData.adults) {
      url.searchParams.set("adults", nextData.adults.toString());
    }

    if (nextData.children) {
      url.searchParams.set("children", nextData.children.toString());
    }

    if (nextData.infants) {
      url.searchParams.set("infants", nextData.infants.toString());
    }

    if (nextData.outbound) {
      url.searchParams.set("from", nextData.outbound.getTime().toString());
    }

    return url;
  }

  function search(): void {
    try {
      goto(getSearchQuery(data));
    } catch {
      //
    }
  }

  function formValid(nextData: Partial<BookingSearchData>): nextData is BookingSearchData {
    return Boolean(
      nextData.origin && nextData.destination && nextData.outbound && (nextData.adults ?? 0) > 0,
    );
  }
</script>

<div class="form-wrapper" class:unset-margin={!firstStep}>
  <div class="search-offers">
    <TextField
      label="From"
      required={firstStep}
      placeholder="City or Station"
      bind:value={data.origin}
      clearable
    />
    <TextField
      label="To"
      required={firstStep}
      placeholder="City or Station"
      bind:value={data.destination}
      clearable
    />

    <DatePicker
      range={false}
      label="Depart"
      bind:value={data.outbound}
      id="depart-date"
      placeholder="Add date"
      required={firstStep}
    />

    <Button on:click={search}>
      <SearchIcon color="var(--color-common-dark-strong)" />
    </Button>
  </div>

  <div class="passenger-select">
    <PassengerPicker
      bind:adults={data.adults}
      bind:children={data.children}
      bind:infants={data.infants}
    />
  </div>
</div>

<style>
  .form-wrapper.unset-margin {
    margin: unset;
    padding: 16px 24px;
    border-radius: unset;
  }

  .form-wrapper {
    margin: 0 24px;
    padding: 24px 24px 16px;
    background: var(--color-common-dark-strong);
    border-radius: 16px;
  }

  .passenger-select {
    margin-top: 16px;
  }

  .search-offers {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr min-content;
    gap: 8px;
    align-items: flex-end;
  }

  .search-offers > :global(.text-field),
  .search-offers > :global(.date-picker) {
    --label-font-size: 16px;
  }
</style>
