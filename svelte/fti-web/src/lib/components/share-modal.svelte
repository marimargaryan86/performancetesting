<script lang="ts">
  import type { FeaturedPackage } from "$lib/models/common";
  import Icon from "$lib/components/icon.svelte";
  import { renderStars } from "$lib/helpers/common";

  type ExtendedFeaturedPackage = FeaturedPackage & {
    images: string[];
  };

  export let show: boolean = false;

  export let hotelInfo: ExtendedFeaturedPackage;

  export let onClose: () => void;

  let isLinkCopied = false;
  let showComingSoonMessage = false;

  const handleShareClick = (platform: string) => {
    const pageURL = window.location.href;

    if (platform === "copyLink") {
      copyLinkToClipBoard(pageURL);
    } else if (platform === "facebook") {
      shareToFacebook();
    } else if (platform === "whatsapp") {
      shareToWhatsApp();
    } else if (platform === "facebook-messenger") {
      shareToFBMessenger();
    } else if (platform === "email") {
      shareToEmail();
    } else if (platform === "messages") {
      shareToMessages();
    }
  };

  const copyLinkToClipBoard = async (url: string) => {
    await navigator.clipboard.writeText(url);
    isLinkCopied = true;
    setTimeout(() => (isLinkCopied = false), 2000);
  };

  const shareToFacebook = async () => {
    await copyLinkToClipBoard(window.location.href);
    const facebookShareUrl = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(window.location.href)}`;
    window.open(facebookShareUrl, "_blank");
  };

  const shareToWhatsApp = () => {
    const message = encodeURIComponent(`Check out this package! ${window.location.href}`);
    const whatsappURL = `https://wa.me/?text=${message}`;
    window.open(whatsappURL, "_blank");
  };

  const shareToFBMessenger = async () => {
    await copyLinkToClipBoard(window.location.href);
    const fbMessengerShareUrl = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(window.location.href)}`;
    window.open(fbMessengerShareUrl, "_blank");
  };

  /**
   * Opens a new tab to compose an email in Gmail with a predefined body containing a link.
   * @param subject (Optional) The subject of the email.
   * @param to (Optional) The recipient's email address.
   */

  const shareToEmail = (subject: string = "", to: string = ""): void => {
    const encodedLink = encodeURIComponent(window.location.href);
    const encodedSubject = encodeURIComponent(subject);
    const encodedTo = encodeURIComponent(to);
    const gmailUrl = `https://mail.google.com/mail/?view=cm&fs=1&tf=1&to=${encodedTo}&su=${encodedSubject}&body=${encodedLink}`;
    window.open(gmailUrl, "_blank");
  };

  const shareToMessages = () => {
    showComingSoonMessage = true;
    setTimeout(() => (showComingSoonMessage = false), 2000);
  };
</script>

<!-- svelte-ignore a11y-no-static-element-interactions -->
{#if show}
  <!-- svelte-ignore a11y-no-static-element-interactions -->
  <!-- svelte-ignore a11y-click-events-have-key-events -->
  <div class="overlay" on:click={onClose}>
    <!-- svelte-ignore a11y-click-events-have-key-events -->
    <!-- svelte-ignore a11y-no-static-element-interactions -->
    <div class="modal-container" on:click|stopPropagation>
      <div class="modal-header">
        <h2>Share Package</h2>
        <button class="close-button" on:click={onClose}>×</button>
      </div>
      <div class="package-details">
        <div class="hotel-image">
          <img src={hotelInfo.images[0]} alt={hotelInfo.name} />
        </div>
        <div class="hotel-info">
          <h3>{hotelInfo.name}</h3>
          <p>
            <Icon variant="location-icon" size="13px" color="#1C1B1F" />
            {hotelInfo.location}
            <img src="/icons/bigxtra-logo-header.svg" alt="" width="23px" height="17.085px" />
          </p>
          <div class="stars">
            {#each renderStars(hotelInfo.stars) as star}
              <span>{star}</span>
            {/each}
          </div>
        </div>
      </div>
      <div class="share-button-container">
        <button class="share-button" on:click={() => handleShareClick("copyLink")}>
          <div class="icon">
            <Icon variant="copy-icon" size="24px" color="black" />
          </div>
          Copy Link
        </button>
        {#if isLinkCopied}
          <div class="copy-confirmation">Package link has been copied to the clipboard!</div>
        {/if}

        <button class="share-button" on:click={() => handleShareClick("email")}>
          <div class="icon">
            <Icon variant="email-icon" size="24px" color="black" />
          </div>
          Email
        </button>
        <button class="share-button" on:click={() => handleShareClick("messages")}>
          <div class="icon">
            <Icon variant="message-icon" size="24px" color="black" />
          </div>
          Messages
        </button>
        <button class="share-button" on:click={() => handleShareClick("whatsapp")}>
          <div class="icon">
            <img src="/icons/whatsapp-icon.svg" alt="" width="24" height="24" />
          </div>
          Whatsapp
        </button>
        <button class="share-button" on:click={() => handleShareClick("facebook")}>
          <div class="icon">
            <img src="/icons/facebook-icon.svg" alt="" width="24" height="24" />
          </div>
          Facebook
        </button>
        <button class="share-button" on:click={() => handleShareClick("facebook-messenger")}>
          <div class="icon">
            <img src="/icons/fb-messenger-icon.svg" alt="" width="24" height="24" />
          </div>
          Messenger
        </button>

        {#if showComingSoonMessage}
          <div class="copy-confirmation">This feature is coming soon!</div>
        {/if}
      </div>
    </div>
  </div>
{/if}

<style>
  .overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: rgba(0, 0, 0, 0.6);
    z-index: 10;
  }

  .modal-container {
    background: #fff;

    display: flex;
    border-radius: 16px;
    padding: 60px;
    width: 80%;
    height: 45%;
    max-width: 675px;
    box-shadow: 0px 8px 16px rgba(0, 0, 0, 0.1);
    flex-direction: column;
    position: relative;
  }

  .modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
  }

  .modal-header h2 {
    color: var(--text-dark, #1c1c1c);
    /* BigXtra/Subheading2 */
    font-family: "Plus Jakarta Sans";
    font-size: 20px;
    font-style: normal;
    font-weight: 600;
    line-height: normal;
    text-transform: capitalize;
  }

  .close-button {
    background: none;
    border: none;
    font-size: 1.5rem;
    cursor: pointer;
  }

  .package-details {
    display: grid;
    grid-template-columns: auto 1fr;
    gap: 16px;
    margin-bottom: 24px;
  }

  .hotel-image img {
    width: 96px;
    height: 64px;
    object-fit: cover;
    border-radius: 8px;
  }

  .hotel-info h3 {
    font-size: 18px;
    font-weight: bold;
    margin: 0;
    color: #333;
  }

  .hotel-info p {
    font-size: 14px;
    margin: 4px 0;
    color: #666;
  }

  .stars {
    color: #f5c518;
  }

  .share-button-container {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    grid-template-rows: repeat(2, 1fr);
    gap: 16px;
  }

  .share-button {
    display: flex;
    padding: 24px;
    justify-content: center;
    align-items: center;
    border: 1px solid var(--strokes-light-stroke, #e3e3e3);
    border-radius: 8px;
    background: #f8f8f8;
    cursor: pointer;
    color: #000;
    font-family: "Plus Jakarta Sans";
    font-size: 16px;
    font-style: normal;
    font-weight: 600;
    line-height: normal;
    width: 220px;
    height: 48px; /* Adjust as needed */
    padding: 0 24px; /* Adjust as needed */
  }

  .share-button:hover {
    background-color: #e8e8e8;
  }

  .icon {
    width: 24px;
    height: 24px;
    margin-right: 15px;
  }
  .copy-confirmation {
    position: absolute;
    bottom: -30px; /* Adjust as needed */
    left: 50%;
    transform: translateX(-50%);
    background-color: #4caf50; /* Green background for success */
    color: white;
    padding: 8px 16px;
    border-radius: 4px;
    font-size: 0.875rem;
    animation: fadeInOut 4s; /* Animation for the confirmation message */
  }

  @keyframes fadeInOut {
    0%,
    100% {
      opacity: 0;
    }
    10%,
    90% {
      opacity: 1;
    }
  }
</style>
