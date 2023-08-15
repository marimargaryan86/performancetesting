import { linear } from "svelte/easing";
import { slide, type SlideParams, type TransitionConfig } from "svelte/transition";

export function slideFade(
  node: Element,
  { delay = 0, duration = 400, easing = linear, axis }: SlideParams = {},
): TransitionConfig {
  const slideCss = slide(node, { axis, delay, duration, easing }).css;

  return {
    delay,
    duration,
    easing,
    css(t, u): string {
      return `${slideCss?.(Math.min(1, t * 2), u)}; opacity: ${Math.max(0, t * 2 - 1)}`;
    },
  };
}
