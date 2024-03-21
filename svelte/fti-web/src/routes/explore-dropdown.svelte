<script lang="ts">
  const holidayTypes = [
    {
      label: "All Inclusive",
      icon: "/icons/wine-icon.svg",
    },
    {
      label: "Family",
      icon: "/icons/family-icon.svg",
    },
    {
      label: "Adults Only",
      icon: "/icons/diamond.svg",
    },
    {
      label: "Tours",
      icon: "/icons/compass.svg",
    },
    {
      label: "City Breaks",
      icon: "/icons/map-icon.svg",
    },
    {
      label: "Winter",
      icon: "/icons/snowflake-icon.svg",
    },
    {
      label: "Long Haul",
      icon: "/icons/palm-icon.svg",
    },
  ];
</script>

<div class="dropdown">
  <div class="holiday-types">
    <div class="label-column">
      <img src="/icons/umbrella.svg" alt="Umbrella" />
      <p>Holiday Types</p>
    </div>
    <div class="content-column">
      <div class="holiday-cards">
        {#each holidayTypes as holidayType}
          <div class="holiday-card">
            <div class="icon">
              <img src={holidayType.icon} alt={holidayType.label} />
            </div>
            <div class="label">{holidayType.label}</div>
          </div>
        {/each}
      </div>
    </div>
  </div>
  <div class="holiday-destinations">
    <div class="label-column">
      <img src="/icons/pin-icon.svg" alt="Pin" />
      <p>By Destination</p>
    </div>
    <div class="content-column">
      <div class="region-columns">
        <div class="region-column">
          <p class="region-title">Europe</p>
          <p class="region-country">Malta</p>
          <p class="region-country">Montenegro</p>
          <p class="region-country">Spain</p>
          <p class="region-country">Turkey</p>
          <p class="region-country">Greece</p>
          <p class="region-country">Cyprus</p>
          <p class="region-country">Italy</p>
        </div>
        <div class="region-column">
          <p class="region-title">Africa / ME</p>
          <p class="region-country">U.A.E</p>
          <p class="region-country">Oman</p>
          <p class="region-country">Morocco</p>
          <p class="region-country">Tunisia</p>
          <p class="region-country">Egypt</p>
        </div>
        <div class="region-column">
          <p class="region-title">Caribbean</p>
          <p class="region-country">Barbados</p>
          <p class="region-country">Cuba</p>
          <p class="region-country">St. Kitts & Nevis</p>
          <p class="region-country">St. Maarten</p>
          <p class="region-country">Jamaica</p>
          <p class="region-country">Aruba</p>
          <p class="region-country">Bahamas</p>
        </div>
        <div class="region-column">
          <p class="region-title">Americas</p>
          <p class="region-country">U.S.A</p>
          <p class="region-country">Mexico</p>
          <p class="region-country">Costa Rica</p>
          <p class="region-country">Belize</p>
          <p class="region-country">Brazil</p>
          <p class="region-country">Argentina</p>
        </div>
        <div class="region-column">
          <p class="region-title">City Breaks</p>
          <p class="region-country">European Breaks</p>
          <p class="region-country">Weekend Deals</p>
          <p class="region-country">City Tours</p>
        </div>
      </div>
    </div>
  </div>
</div>

<style>
  .dropdown {
    display: flex;
    flex-direction: column;
    gap: 40px;
    padding: 46px 60px;
  }

  .holiday-types {
    display: flex;
    flex-direction: row;
    gap: 60px;
  }

  .holiday-destinations {
    display: flex;
    flex-direction: row;
    gap: 60px;
  }

  .holiday-types .label-column,
  .holiday-destinations .label-column {
    display: flex;
    flex-direction: row;
    gap: 4px;
    align-items: flex-start;
    justify-content: center;
  }

  .label-column p {
    width: 150px;
    color: #363636;
    font-weight: 700;
    font-size: 16px;
    font-style: normal;
    line-height: 16.8px;
  }

  .label-column img {
    margin: 13px 0;
  }

  .region-columns {
    display: flex;
    flex-direction: row;
    gap: 70px;
  }

  .holiday-cards {
    display: flex;
    flex-direction: row;
    gap: 16px;
  }

  .holiday-card {
    display: flex;
    flex-direction: column;
    gap: 16px;
    align-items: center;
    justify-content: center;
    width: 100px;
    padding: 24px 10px;
    background: #fbeadd;
    border-radius: 4px;
  }

  .holiday-card > .label {
    color: #ea7121;
    font-weight: 500;
    font-size: 14px;
    font-style: normal;
    line-height: 16.8px; /* 120% */
    text-align: center;
  }

  .region-title {
    color: #000000;
    font-weight: 700;
    font-size: 16px;
    font-style: normal;
    line-height: 16.8px;
  }
</style>
