<script lang="ts" context="module">
  import ChevronIcon from "components/icons/chevron-icon.svelte";
  import { slideFade } from "transitions/slide-fade";

  const items = [
    {
      question: "What train operators are available through Junction Hub?",
      answer:
        "Junction Hub gives you access to a host of rail journeys across Europe, aboard operators such as Eurostar, SNCF, Thalys, Deutsche Bahn and more.",
    },
    {
      question: "Can I view and compare different journey times and prices in one place?",
      answer:
        "By searching in Junction Hub, you can easily see all of the available departures for your chosen travel dates, and compare the different fare types and prices on your customers’ behalf.",
    },
    {
      question: "What payment options are accepted?",
      answer: "Currently all booking payments are made using your agency credit card.",
    },
    {
      question: "How do I cancel bookings in Junction Hub?",
      answer:
        "To cancel a booking, you will need to make a cancellation request. Take a look at our user guide, or watch our short video tutorial, for more information on how to cancel a booking in Junction Hub.",
    },
    {
      question: "How do I access customers’ train tickets?",
      answer:
        "Navigate to the “Orders” tab, where you can view all existing orders and their status. To download your customers’ tickets, select their order and click on the “Download ticket” link.",
    },
    {
      question: "How do I contact customer support?",
      answer:
        "The Snowfall support team is on hand to help if you have any issues. Simply email support@snowfalltravel.com.",
    },
  ];
</script>

<script lang="ts">
  let expandedIdx: number | undefined;

  function expand(index: number): void {
    expandedIdx = expandedIdx === index ? undefined : index;
  }
</script>

<section>
  <h2 class="typography headline-large bold">Frequently Asked Questions</h2>

  <ol>
    {#each items as item, idx}
      {@const expanded = expandedIdx === idx}

      <li>
        <div>
          <strong class="typography title-medium bold">
            {idx + 1}. {item.question}
          </strong>

          {#if expanded}
            <p class="typography body-large" transition:slideFade={{ duration: 400 }}>
              {item.answer}
            </p>
          {/if}
        </div>

        <button on:click={expand.bind(expand, idx)}>
          <ChevronIcon
            direction={expanded ? "up" : "down"}
            size="32px"
            color="var(--color-main-primary-500)"
          />
        </button>
      </li>
    {/each}
  </ol>
</section>

<style>
  section {
    display: flex;
    flex-flow: column;
    gap: 48px;
    padding-top: 72px;
  }

  h2 {
    text-align: center;
  }

  ol {
    display: flex;
    flex-flow: column;
    gap: 16px;
  }

  li {
    display: flex;
    gap: 16px;
    align-items: center;
    padding: 32px 24px;
    background-color: var(--color-common-background-light-main);
    border-radius: 12px;
  }

  li > div {
    flex-grow: 1;
  }

  li > div > p {
    padding-top: 16px;
    color: var(--color-common-light-medium);
  }

  button {
    height: 24px;
    padding: 0;
    background-color: transparent;
    border: 0;
    cursor: pointer;
  }

  button > :global(svg) {
    vertical-align: top;
  }
</style>
