<script lang="ts">
</script>

<input type="checkbox" role="switch" class="basic" />

<style>
  .basic {
    position: relative;
    width: 3em;
    height: 30px;
    margin: 0 15px;
    font-size: 1em;
    background: var(--colours-primary-orange);
    border: none;
    border-radius: 2em;
    appearance: none;
    aspect-ratio: 2;
  }

  .basic::before {
    position: absolute;
    top: 50%;
    left: 31%;
    box-sizing: border-box;
    width: 25px;
    height: 25px;
    background: white;
    border: 1px solid #ffffff;
    border-radius: 50%;
    transform: translate(-50%, -50%);
    transition: left 0.5s;
    content: "";
  }

  .basic:checked {
    &::before {
      left: 75%;
    }
  }
</style>
