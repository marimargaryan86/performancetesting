<script lang="ts">
</script>

<div class="lds-ring">
  <div></div>
  <div></div>
  <div></div>
  <div></div>
</div>

<style>
  .lds-ring {
    position: relative;
    display: inline-block;
    width: 40px;
    height: 40px;
  }

  .lds-ring div {
    position: absolute;
    display: block;
    box-sizing: border-box;
    width: 50px;
    height: 50px;
    margin: 8px;
    border: 7px solid #ffffff;
    border-color: #11adcf transparent transparent;
    border-radius: 50%;
    animation: lds-ring 1.2s cubic-bezier(0.5, 0, 0.5, 1) infinite;
  }

  .lds-ring div:nth-child(1) {
    animation-delay: -0.45s;
  }

  .lds-ring div:nth-child(2) {
    animation-delay: -0.3s;
  }

  .lds-ring div:nth-child(3) {
    animation-delay: -0.15s;
  }

  @keyframes lds-ring {
    0% {
      transform: rotate(0deg);
    }

    100% {
      transform: rotate(360deg);
    }
  }
</style>
