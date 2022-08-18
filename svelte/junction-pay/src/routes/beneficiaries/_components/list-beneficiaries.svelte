<script lang="ts">
  import Table from "$lib/components/table.svelte";
  import { openPopup } from "../../../lib/stores";

  function deleteBeneficiary() {
    openPopup({
      title: "Delete beneficiary",
      options: {
        message: "Are you sure you want to delete beneficiary",
        showConfirmButton: true,
        showCancelButton: true,
      },
    });
  }

  function editBeneficiary() {
    // TODO: Impl.
  }
</script>

<div class="sub-accounts">
  <div class="letters">
    <div class="letter">A</div>
    <div class="letter">B</div>
    <div class="letter">C</div>
  </div>
  <Table>
    <thead>
      <tr>
        <th>Beneficiary</th>
        <th>Currency</th>
        <th>Bank Country</th>
        <th>Type</th>
        <th>Actions</th>
      </tr>
    </thead>
    {#each [[{ bank_account_holder_name: "Asd", currency: "Asd", bank_country: "Asd", payment_types: ["Asd"] }]] as beneficiary}
      <tbody>
        <h1 class="letter-tag">{beneficiary[0].bank_account_holder_name[0].toUpperCase()}</h1>
        {#each beneficiary as row}
          <tr>
            <td>{row.bank_account_holder_name}</td>
            <td>{row.currency}</td>
            <td>{row.bank_country}</td>
            <td>{row.payment_types[0]}</td>
            <td>
              <img
                on:click={() => {
                  editBeneficiary();
                }}
                src="/images/icons/edit-icon.png"
                alt="edit button"
              />
              <img
                on:click={() => {
                  deleteBeneficiary();
                }}
                src="/images/icons/delete-icon.png"
                alt="delete button"
              />
            </td>
          </tr>
        {:else}
          <p>LOAD</p>
        {/each}
      </tbody>
    {:else}
      <p>Loading</p>
    {/each}
  </Table>
</div>

<style>
  .sub-accounts {
    margin-top: 56px;
  }

  .letters {
    display: flex;
    position: sticky;
  }

  .sub-accounts :global(table) {
    width: 100%;
  }

  thead {
    width: 100%;
  }

  .letter-tag {
    font-size: 25px;
    font-weight: 400;
    margin: 16px 0;
  }

  img {
    height: 28px;
    padding: 4px 8px;
  }

  img:hover {
    cursor: pointer;
  }

  tr td:first-of-type::first-letter {
    text-transform: uppercase;
  }

  thead tr th {
    color: #03251b;
  }

  tbody tr td {
    padding: 10px 20px;
  }

  tbody tr:first-of-type td:first-of-type {
    border-top-left-radius: 10px;
  }

  tbody tr:first-of-type td:last-of-type {
    border-top-right-radius: 10px;
  }
</style>
