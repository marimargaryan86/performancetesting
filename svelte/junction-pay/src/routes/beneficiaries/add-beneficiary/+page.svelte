<script lang="ts">
  import { goto } from "$app/navigation";
  import type { BeneficiaryPutModel } from "$integration/currency-cloud/models/beneficiaries/common";
  import type { RequirementsModel } from "$integration/currency-cloud/models/beneficiaries/requirements";
  import type {
    RecursivePartial,
    ValidationError,
  } from "$integration/currency-cloud/models/common";
  import type { CurrencyModel } from "$integration/currency-cloud/models/currencies";
  import type { EntityType, PaymentType } from "$integration/currency-cloud/schemas/beneficiaries";
  import Button from "$lib/components/button.svelte";
  import Checkbox from "$lib/components/checkbox.svelte";
  import DatePicker from "$lib/components/date-picker/date-picker.svelte";
  import PatternedTextField from "$lib/components/patterned-text-field.svelte";
  import Radio from "$lib/components/radio.svelte";
  import SelectField from "$lib/components/select-field.svelte";
  import TextField from "$lib/components/text-field.svelte";
  import routeConfig from "$lib/route-config";
  import { currencyStore, countryStore } from "$lib/stores";
  import type { CountryModel } from "$models/location-models";
  import instances from "$services/instances";
  import { onMount } from "svelte";
  import Layout from "../layout.svelte";

  let data: BeneficiaryPutModel = {
    bank: {
      account: {
        currencyCode: "",
        holderName: "",
      },
      countryCode: "",
    },
    nickname: "",
    default: false,
    entityType: "company",
    paymentTypes: ["regular"],
  };

  let errors: ValidationError<BeneficiaryPutModel> = {};

  let company: {
    name?: string;
    registrationDate?: Date;
  } = {};
  let individual: {
    firstName?: string;
    lastName?: string;
    birthDate?: Date;
  } = {};
  let contact: {
    email?: string;
    postalCode?: string;
    city?: string;
    countryCode?: string;
    stateOrProvince?: string;
    externalReference?: string;
    address?: string;
  } = {};
  let currencies: CurrencyModel[] = [];
  let countries: CountryModel[] = [];
  let currency: CurrencyModel | undefined = undefined;
  let bankAccountCountry: CountryModel | undefined = undefined;
  let contactCountry: CountryModel | undefined = undefined;
  let entityType: EntityType = "company";
  let paymentTypes: PaymentType[] = data.paymentTypes ?? [];
  let prevSearch = `${currency}-${bankAccountCountry}-${contactCountry}-${entityType}-${paymentTypes.join(
    ", ",
  )}`;
  let requirementsList: RequirementsModel[] = [];
  let minimumRequirements: RecursivePartial<RequirementsModel> = {};

  $: companyErrors = (errors as ValidationError<BeneficiaryPutModel<"company">>)?.company;
  $: individualErrors = (errors as ValidationError<BeneficiaryPutModel<"individual">>)?.individual;
  $: data.contact = contact;
  $: if (data.entityType === "company") {
    data.company = company;
  } else if (data.entityType === "individual") {
    data.individual = individual;
  }
  $: data.bank.account.currencyCode = currency?.code ?? data.bank.account.currencyCode;
  $: data.bank.countryCode = bankAccountCountry?.code ?? data.bank.countryCode;
  $: contact.countryCode = contactCountry?.code;
  $: data.entityType = entityType;
  $: data.paymentTypes = [...paymentTypes];
  $: {
    const nextSearch = `${currency?.code}-${bankAccountCountry?.code}-${
      contactCountry?.code
    }-${entityType}-${paymentTypes.join(", ")}`;

    if (nextSearch !== prevSearch) {
      prevSearch = nextSearch;
      updateRequirements();
    }
  }
  $: {
    let nextRequirements: RecursivePartial<RequirementsModel> = {
      entityType,
      bank: {
        account: {
          bic: true,
          iban: true,
          number: true,
          sortCode: true,
        },
      },
      contact: {
        address: true,
        city: true,
        countryCode: true,
        postalCode: true,
        stateOrProvince: true,
      },
      company: {
        name: true,
        registrationDate: true,
      },
      individual: {
        birthDate: true,
        firstName: true,
        lastName: true,
      },
    };

    if (!requirementsList.length) {
      minimumRequirements = {};
    } else {
      requirementsList.forEach((requirements) => {
        nextRequirements = consolidate(nextRequirements, requirements);
      });

      minimumRequirements = nextRequirements;
    }
  }
  $: required = {
    company:
      minimumRequirements.entityType === "company"
        ? {
            name: minimumRequirements.company?.name,
            registrationDate: minimumRequirements.company?.registrationDate,
          }
        : undefined,
    individual:
      minimumRequirements.entityType === "individual"
        ? {
            firstName: minimumRequirements.individual?.firstName,
            lastName: minimumRequirements.individual?.lastName,
            birthDate: minimumRequirements.individual?.birthDate,
          }
        : undefined,
    bank: {
      account: {
        number: minimumRequirements.bank?.account?.number,
        iban: minimumRequirements.bank?.account?.iban,
        sortCode: minimumRequirements.bank?.account?.sortCode,
        bic: minimumRequirements.bank?.account?.bic,
      },
    },
    contact: {
      address: minimumRequirements.contact?.address,
      postalCode: minimumRequirements.contact?.postalCode,
      city: minimumRequirements.contact?.city,
      stateOrProvince: minimumRequirements.contact?.stateOrProvince,
      countryCode: minimumRequirements.contact?.countryCode,
    },
  };

  function consolidate<T1 extends object | boolean, T2 extends object | boolean>(
    value1: T1,
    value2: T2,
  ): T1 {
    if (typeof value1 === "object" && typeof value2 === "object") {
      return Object.fromEntries(
        Object.entries(value1).map(([key, value]) => [
          key,
          consolidate(value, value2[key as keyof typeof value2] as T2),
        ]),
      ) as T1;
    } else {
      return (value1 && value2) as unknown as T1;
    }
  }

  async function updateRequirements(): Promise<void> {
    if (!(currency && bankAccountCountry)) {
      requirementsList = [];

      return;
    }

    requirementsList = await instances.beneficiary.getRequirements(
      bankAccountCountry.code,
      currency.code,
      contactCountry?.code,
      entityType,
      paymentTypes,
    );
  }

  async function submit(): Promise<void> {
    errors = {};

    try {
      await instances.beneficiary.create(data);

      goto(routeConfig.beneficiaries.root);
    } catch (error) {
      if (error === "BAD_REQUEST") {
        return;
      }

      if (typeof error === "object") {
        errors = error as ValidationError<BeneficiaryPutModel>;
      }
    }
  }

  onMount(async () => {
    currencies = await $currencyStore;
    countries = await $countryStore;
    currency = currencies.find((item) => item.code === data.bank.account.currencyCode);
    contactCountry = countries.find((item) => item.code === data.contact?.countryCode);
    bankAccountCountry = countries.find((item) => item.code === data.bank.countryCode);
  });
</script>

<svelte:head>
  <title>Junction | Add beneficiary</title>
</svelte:head>

<Layout>
  <form class="add-beneficiary" slot="body" on:submit|preventDefault={submit}>
    <fieldset>
      <h1>Add benficiary</h1>
      <div>
        <label for="nickname" class:error={errors?.nickname}>Nickname*:</label>
        <TextField id="nickname" bind:value={data.nickname} error={errors?.nickname?.join(", ")} />
      </div>
    </fieldset>

    <fieldset>
      <h2 class:error={errors?.entityType}>Beneficiary type</h2>

      <ul>
        <li>
          <label for="entity-company">
            <Radio id="entity-company" value="company" bind:group={entityType} />
            <span>Company</span>
          </label>
        </li>

        <li>
          <label for="entity-individual">
            <Radio id="entity-individual" value="individual" bind:group={entityType} />
            <span>Individual</span>
          </label>
        </li>
      </ul>
    </fieldset>

    <fieldset>
      <h2 class:error={errors?.paymentTypes}>Payment types*</h2>
      <ul>
        <li>
          <label for="payment-regular">
            <Checkbox id="payment-regular" value="regular" bind:group={paymentTypes} />
            <span>Regular</span>
          </label>
        </li>

        <li>
          <label for="payment-priority">
            <Checkbox id="payment-priority" value="priority" bind:group={paymentTypes} />
            <span>Priority</span>
          </label>
        </li>
      </ul>
    </fieldset>

    <fieldset>
      <h2>Bank account details</h2>

      <div>
        <label for="currency" class:error={errors?.bank?.account?.currencyCode}>Currency*:</label>
        <SelectField
          id="currency"
          bind:value={currency}
          items={currencies}
          displayValue={(item) => (item ? `(${item.code}) ${item.name}` : "")}
          error={errors?.bank?.account?.currencyCode?.join(", ")}
        />
      </div>

      <div>
        <label for="bank-account-country" class:error={errors?.bank?.countryCode}>Country*:</label>
        <SelectField
          id="bank-account-country"
          bind:value={bankAccountCountry}
          items={countries}
          displayValue={(item) => item?.name ?? ""}
          error={errors?.bank?.countryCode?.join(", ")}
        />
      </div>

      <div>
        <label for="account-number" class:error={errors?.bank?.account?.holderName}>
          Holder name*:
        </label>
        <TextField
          id="account-number"
          bind:value={data.bank.account.holderName}
          error={errors?.bank?.account?.holderName?.join(", ")}
        />
      </div>

      <div>
        <label for="account-number" class:error={errors?.bank?.account?.number}>
          Account number{required.bank.account.number ? "*" : ""}:
        </label>
        <TextField
          id="account-number"
          bind:value={data.bank.account.number}
          error={errors?.bank?.account?.number?.join(", ")}
        />
      </div>

      <div>
        <label for="bic" class:error={errors?.entityType}>
          BIC/SWIFT{required.bank.account.bic ? "*" : ""}:
        </label>
        <TextField
          id="bic"
          bind:value={data.bank.account.bic}
          error={errors?.bank?.account?.bic?.join(", ")}
        />
      </div>

      <div>
        <label for="sort-code" class:error={errors?.bank?.account?.sortCode}>
          Sort code{required.bank.account.sortCode ? "*" : ""}:
        </label>
        <PatternedTextField
          pattern="99-99-99"
          id="sort-code"
          bind:value={data.bank.account.sortCode}
          error={errors?.bank?.account?.sortCode?.join(", ")}
        />
      </div>

      <div>
        <label for="iban" class:error={errors?.bank?.account?.iban}>
          IBAN{required.bank.account.iban ? "*" : ""}:
        </label>
        <TextField
          id="iban"
          bind:value={data.bank.account.iban}
          error={errors?.bank?.account?.iban?.join(", ")}
        />
      </div>
    </fieldset>

    <fieldset>
      <h2>Contact details</h2>

      <div>
        <label for="contact-country" class:error={errors?.contact?.countryCode}>
          Country{required.contact.countryCode ? "*" : ""}:
        </label>
        <SelectField
          id="contact-country"
          bind:value={contactCountry}
          items={countries}
          displayValue={(item) => item?.name ?? ""}
          error={errors?.contact?.countryCode?.join(", ")}
        />
      </div>

      <div>
        <label for="state-or-province" class:error={errors?.contact?.stateOrProvince}>
          State/Province{required.contact?.stateOrProvince ? "*" : ""}:
        </label>
        <TextField
          id="state-or-province"
          bind:value={contact.stateOrProvince}
          error={errors?.contact?.stateOrProvince?.join(", ")}
        />
      </div>

      <div>
        <label for="city" class:error={errors?.contact?.city}>
          City{required.contact?.city ? "*" : ""}:
        </label>
        <TextField id="city" bind:value={contact.city} error={errors?.contact?.city?.join(", ")} />
      </div>

      <div>
        <label for="postal-code" class:error={errors?.contact?.postalCode}>
          Postal code{required.contact?.postalCode ? "*" : ""}:
        </label>
        <TextField
          id="postal-code"
          bind:value={contact.postalCode}
          error={errors?.contact?.postalCode?.join(", ")}
        />
      </div>

      <div>
        <label for="address" class:error={errors?.contact?.address}>
          Address{required.contact?.address ? "*" : ""}:
        </label>
        <TextField
          id="address"
          bind:value={contact.address}
          error={errors?.contact?.address?.join(", ")}
        />
      </div>

      <div>
        <label for="email" class:error={errors?.contact?.email}>E-mail:</label>
        <TextField
          id="email"
          bind:value={contact.email}
          error={errors?.contact?.email?.join(", ")}
        />
      </div>
    </fieldset>

    {#if data.entityType === "company"}
      <fieldset>
        <h2>Company details</h2>

        <div>
          <label for="company-name" class:error={companyErrors?.name}>
            Company name{required.company?.name ? "*" : ""}:
          </label>
          <TextField
            id="company-name"
            bind:value={company.name}
            error={companyErrors?.name?.join("; ")}
          />
        </div>

        <div>
          <label for="registration-date" class:error={companyErrors?.registrationDate}>
            Registration date{required.company?.registrationDate ? "*" : ""}:
          </label>
          <DatePicker
            id="registration-date"
            bind:start={company.registrationDate}
            error={companyErrors?.registrationDate?.join(", ")}
          />
        </div>
      </fieldset>
    {:else if data.entityType === "individual"}
      <fieldset>
        <h2>Individual details</h2>

        <div>
          <label for="first-name" class:error={individualErrors?.firstName}>
            First name{required.individual?.firstName ? "*" : ""}:
          </label>
          <TextField
            id="first-name"
            bind:value={individual.firstName}
            error={individualErrors?.firstName?.join(", ")}
          />
        </div>

        <div>
          <label for="last-name" class:error={individualErrors?.lastName}>
            Last name{required.individual?.lastName ? "*" : ""}:
          </label>
          <TextField
            id="last-name"
            bind:value={individual.lastName}
            error={individualErrors?.lastName?.join(", ")}
          />
        </div>

        <div>
          <label for="birth-date" class:error={individualErrors?.birthDate}>
            Birth date{required.individual?.birthDate ? "*" : ""}:
          </label>
          <DatePicker
            id="birth-date"
            bind:start={individual.birthDate}
            error={individualErrors?.birthDate?.join(", ")}
          />
        </div>
      </fieldset>
    {/if}

    <Button type="submit">Create</Button>
  </form>
</Layout>

<style>
  .add-beneficiary {
    margin: 0 auto;
    max-width: 1080px;
    padding: 0 49px 30px;
    width: 100%;
  }

  fieldset {
    display: grid;
    gap: 16px;
    grid-template-columns: 1fr 1fr;
    margin: 0 0 40px;
  }

  div > label {
    display: block;
    margin-bottom: 8px;
    padding-left: 8px;
  }

  div > :global(.text-field),
  div > :global(.select-field),
  div > :global(.date-picker) {
    box-shadow: 0 4px 30px rgb(0 0 0 / 8%);
    width: 100%;
  }

  label > :global(.checkbox),
  label > :global(.radio) {
    margin-right: 4px;
    vertical-align: middle;
  }

  h1 {
    font-size: 24px;
    font-weight: 600;
    grid-column: 1 / -1;
    margin-bottom: 8px;
  }

  h2 {
    font-size: 18px;
    font-weight: 500;
    grid-column: 1 / -1;
    margin-bottom: 8px;
  }

  ul {
    padding-left: 8px;
  }

  li {
    display: inline-block;
    margin-left: -8px;
    margin-right: 24px;
  }

  .error {
    color: var(--color-red);
  }

  .add-beneficiary > :global(button) {
    background-color: var(--color-orange);
    float: right;
    padding-left: 24px;
    padding-right: 24px;
  }
</style>
