<script lang="ts">
  import type { TransitionConfig } from "svelte/transition";

  type TransitionParams = $$Generic<unknown>;

  type Transition<U, T = (node: Element, params: U) => TransitionConfig> = {
    func: T;
    params: U;
  };

  let _transition: Transition<TransitionParams> | undefined = undefined;
  export { _transition as transition };

  function transition(node: Element): TransitionConfig {
    return _transition?.func(node, _transition.params) ?? { duration: 0 };
  }
</script>

<svg
  transition:transition|local
  width="16"
  height="16"
  viewBox="0 0 16 16"
  fill="none"
  xmlns="http://www.w3.org/2000/svg"
  class="spinner"
>
  <path
    d="M8 1C6.14348 1 4.36301 1.7375 3.05025 3.05026C1.7375 4.36301 1 6.14349 1 8C1 8.13261 0.947321 8.25979 0.853553 8.35356C0.759785 8.44733 0.632608 8.5 0.5 8.5C0.367392 8.5 0.240215 8.44733 0.146447 8.35356C0.0526785 8.25979 0 8.13261 0 8C0 6.41775 0.469192 4.87103 1.34824 3.55544C2.22729 2.23985 3.47672 1.21447 4.93853 0.608967C6.40034 0.00346625 8.00887 -0.15496 9.56072 0.153721C11.1126 0.462403 12.538 1.22433 13.6569 2.34315C14.7757 3.46197 15.5376 4.88743 15.8463 6.43928C16.155 7.99113 15.9965 9.59966 15.391 11.0615C14.7855 12.5233 13.7602 13.7727 12.4446 14.6518C11.129 15.5308 9.58225 16 8 16C7.86739 16 7.74021 15.9473 7.64645 15.8536C7.55268 15.7598 7.5 15.6326 7.5 15.5C7.5 15.3674 7.55268 15.2402 7.64645 15.1465C7.74021 15.0527 7.86739 15 8 15C8.91925 15 9.82951 14.8189 10.6788 14.4672C11.5281 14.1154 12.2997 13.5998 12.9497 12.9498C13.5998 12.2997 14.1154 11.5281 14.4672 10.6788C14.8189 9.82951 15 8.91926 15 8C15 7.08075 14.8189 6.1705 14.4672 5.32122C14.1154 4.47194 13.5998 3.70027 12.9497 3.05026C12.2997 2.40025 11.5281 1.88463 10.6788 1.53285C9.82951 1.18106 8.91925 1 8 1V1Z"
    fill="white"
  />
</svg>

<style>
  .spinner {
    animation: rotate 800ms ease infinite;
  }

  @keyframes rotate {
    0% {
      transform: rotateZ(0deg);
    }

    100% {
      transform: rotateZ(360deg);
    }
  }
</style>
