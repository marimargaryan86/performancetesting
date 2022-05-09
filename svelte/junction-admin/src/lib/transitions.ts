import { cubicOut } from "svelte/easing";
import { slide as slide_ } from "svelte/transition";
import type { SlideParams as SlideParams_, TransitionConfig } from "svelte/transition";

export type SlideParams = SlideParams_ & {
  direction?: "horizontal" | "vertical";
};

export function slide(
  node: Element,
  { delay = 0, duration = 400, easing = cubicOut, direction = "vertical" }: SlideParams = {},
): TransitionConfig {
  if (direction === "vertical") {
    return slide_(node, { delay, duration, easing });
  }

  const style = getComputedStyle(node);
  const opacity = +style.opacity;
  const width = parseFloat(style.width);
  const paddingLeft = parseFloat(style.paddingLeft);
  const paddingRight = parseFloat(style.paddingRight);
  const marginLeft = parseFloat(style.marginLeft);
  const marginRight = parseFloat(style.marginRight);
  const borderLeftWidth = parseFloat(style.borderLeftWidth);
  const borderRightWidth = parseFloat(style.borderRightWidth);

  return {
    delay,
    duration,
    easing,
    css: (t) =>
      "overflow: hidden;" +
      `opacity: ${Math.min(t * 20, 1) * opacity};` +
      `width: ${t * width}px;` +
      `padding-left: ${t * paddingLeft}px;` +
      `padding-right: ${t * paddingRight}px;` +
      `margin-left: ${t * marginLeft}px;` +
      `margin-right: ${t * marginRight}px;` +
      `border-left-width: ${t * borderLeftWidth}px;` +
      `border-right-width: ${t * borderRightWidth}px;`,
  };
}

export function conditional<T = Record<string, unknown>, U = Element>(
  node: U,
  args: {
    params: T;
    transition: (node: U, params: T) => TransitionConfig;
  },
): TransitionConfig {
  return args.transition(node, args.params);
}
