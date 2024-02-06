<script lang="ts" context="module">
  let railServices = [
    {
      name: "CFL Luxembourg",
      link: "French version",
      url: "https://www.cfl.lu/en-gb/legalinfos/detail/conditions-de-transport-internationaux",
    },
    {
      name: "Deutsche Bahn - ICE and Regional",
      link: "English version",
      url: "https://int.bahn.de/en/gtc",
    },
    {
      name: "Eurostar",
      link: "English version",
      url: "https://www.eurostar.com/uk-en/conditions-carriage",
    },
    {
      name: "OBB Austria",
      link: "English version",
      url: "https://www.oebb.at/static/tarife/en/guide_for_travelling_with_oebb_in_austria/Resources/pdf/1501696139__en.pdf",
    },
    {
      name: "SBB Switzerland",
      link: "English version",
      url: "https://www.sbb.ch/en/travelcards-and-tickets/tickets-for-switzerland/tickets-europe/conditions.html",
    },
    {
      name: "SNCB",
      link: "English version",
      url: "https://www.belgiantrain.be/en/support/terms-and-conditions-for-transport",
    },
    {
      name: "SNCF",
      link: "English version",
      url: "https://www.sncf-connect.com/en-en/help/conditions",
    },
    {
      name: "Thalys",
      link: "English version",
      url: "https://www.thalys.com/sites/thalys.com/files/legal/NEW/CG_Transports_EN.pdf",
    },
    { name: "NS", link: "English version", url: "https://www.ns.nl/en/terms-conditions.html" },
    {
      name: "NTV Itaio",
      link: "English version",
      url: "https://www.italotreno.it/~/media/Images/content/pdf/contratto_di_trasporto/Contrattoditrasportorel604_eng#:~:text=The%20Passenger%20is%20obliged%20to,train%20without%20a%20valid%20Ticket.",
    },
    {
      name: "Tranitalia Italy",
      link: "English version",
      url: "https://www.trenitalia.com/content/dam/tcom/tfrance/attachments/CGVT%20Trenitalia%20France_France_avril2022_EN.pdf",
    },
    {
      name: "CD Czech Railways",
      link: "English version",
      url: "https://www.cd.cz/assets/info/cim-se-ridime/cd-contractual-and-transport-terms-for-public-passenger-railway-transport-_sppo_.pdf",
    },
    {
      name: "NSB VY Norway",
      link: "English version",
      url: "https://www.vy.no/en/conditions-and-privacy/conditions-of-carriage",
    },
    {
      name: "SJ Sweden",
      link: "English version",
      url: "https://www.sj.se/en/travel-terms/general-terms-and-conditions-of-travel.html",
    },
  ];
</script>

<script lang="ts">
  import { getTranslator } from "~/i18n";

  const t = getTranslator();
</script>

<div>
  <!-- eslint-disable-next-line svelte/no-at-html-tags -->
  {@html $t("pages.help.pages.conditionsOfCarriage.content")}

  <ul>
    {#each railServices as service}
      <li>
        {service.name} (<a href={service.url} target="_blank">{service.link}</a>)
      </li>
    {/each}
  </ul>
</div>

<style>
  div {
    display: flex;
    flex-flow: column;
    gap: 16px;
  }

  ul {
    display: flex;
    flex-flow: column;
    gap: 4px;
    padding-left: 16px;
    color: var(--color-main-primary-900);
    list-style-type: disc;
  }

  a {
    color: var(--color-common-light-text-link);
    text-decoration: none;
  }
</style>
