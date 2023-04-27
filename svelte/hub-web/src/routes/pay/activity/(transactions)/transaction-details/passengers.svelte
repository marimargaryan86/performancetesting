<script lang="ts">
  import { yymmdd } from "formatting/date-time";

  const passengers = [
    {
      firstName: "Jonathan",
      lastName: "Smith",
      email: "john.smith@example.com",
      gender: "Male",
      dateOfBirth: new Date(),
    },
    {
      firstName: "Mary",
      lastName: "Smith",
      email: "mary.smith@example.com",
      gender: "Female",
      dateOfBirth: new Date(),
    },
    {
      firstName: "Martin",
      lastName: "Smith",
      email: "martin.smith@example.com",
      gender: "Male",
      dateOfBirth: new Date(),
    },
  ];
</script>

<div class="passengers">
  <h3 class="typography title-medium bold">Passengers</h3>

  <div class="list">
    {#each passengers as passenger}
      <span class="typography body-small subtle">First Name</span>
      <span class="typography body-small subtle">Last Name</span>
      <span class="typography body-small subtle">Gender</span>
      <span class="typography body-small subtle">DOB</span>
      <strong class="typography body-small bold">{passenger.firstName}</strong>
      <strong class="typography body-small bold">{passenger.lastName}</strong>
      <strong class="typography body-small bold">{passenger.gender}</strong>
      <strong class="typography body-small bold">{yymmdd(passenger.dateOfBirth)}</strong>
      <strong class="typography body-small subtle email">{passenger.email}</strong>
    {/each}
  </div>
</div>

<style>
  .passengers {
    padding: 24px;
    color: var(--color-main-neutral-800);
    border: var(--color-main-neutral-200) 1px solid;
    border-radius: 16px;
  }

  h3 {
    margin-bottom: 24px;
  }

  .list {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 4px 8px;
  }

  .email {
    grid-column: 1 / -1;
  }

  .email:not(:last-child) {
    margin-bottom: 24px;
  }

  .subtle {
    color: var(--color-main-neutral-500);
  }
</style>
