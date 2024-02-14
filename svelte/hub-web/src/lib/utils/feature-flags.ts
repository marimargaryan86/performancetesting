import { getContext, setContext } from "svelte";
import { writable, type Readable, type Writable, derived } from "svelte/store";
import type * as OrySchemas from "~/integration/ory/schemas";

type DateString = `${number}-${number}-${number}`;
type HasFeatureFunc = (feature: Feature) => boolean;
type ToggleFeatureFunc = (feature: Feature) => void;
type FeatureTools = {
  hasFeature: HasFeatureFunc;
  toggleFeature: ToggleFeatureFunc;
};

export const enum Feature {
  DEV_TOOLS = "dev-tools",
  OFFERS_TIME_WINDOWS = "offers-time-windows",
}

export const FEATURES: Record<
  Feature,
  {
    owner: string;
    description?: string;
    releaseDate: DateString | "always";
    removalDate: DateString | "never";
  }
> = {
  [Feature.DEV_TOOLS]: {
    owner: "Everyone",
    description: "Enables dev tools",
    releaseDate: "always",
    removalDate: "never",
  },
  [Feature.OFFERS_TIME_WINDOWS]: {
    owner: "Marcus Ewall <marcus.e@snowfalltravel.com>",
    description: "Enables time windows in search for offers",
    releaseDate: "2024-02-29",
    removalDate: "2024-05-29",
  },
};

export type Features = Partial<typeof FEATURES>;

const FEATURES_CTX_KEY = "features";
const ENABLED_FEATURES_CTX_KEY = "enabled-features";
const FEATURE_TOOLS_CTX_KEY = "feature-tools";

function setFeatureTools(enabledFeaturesCtx: Writable<Feature[]>): Writable<FeatureTools> {
  return setContext(
    FEATURE_TOOLS_CTX_KEY,
    writable<FeatureTools>(undefined, (set) => {
      return enabledFeaturesCtx.subscribe((enabledFeatures) => {
        set({
          hasFeature: (feature) => enabledFeatures.includes(feature),
          toggleFeature: (feature): void => {
            if (enabledFeatures.includes(feature)) {
              enabledFeaturesCtx.set(enabledFeatures.filter((item) => item !== feature));
            } else {
              enabledFeaturesCtx.set([...enabledFeatures, feature]);
            }
          },
        });
      });
    }),
  );
}

export function getFeatureTools(): Readable<FeatureTools> {
  return getContext(FEATURE_TOOLS_CTX_KEY);
}

export function setFeatures(features: Features): Writable<Features> {
  const featuresCtx = setContext(FEATURES_CTX_KEY, writable<Features>(features));
  const enabledFeaturesCtx = setContext(
    ENABLED_FEATURES_CTX_KEY,
    writable(Object.keys(features) as Feature[]),
  );

  setFeatureTools(enabledFeaturesCtx);

  return featuresCtx;
}

export function getFeatures(): Readable<{
  [key in keyof Features]: Features[key] & { enabled: boolean };
}> {
  const featuresCtx = getContext<Readable<Features>>(FEATURES_CTX_KEY);
  const enabledFeaturesCtx = getContext<Readable<Feature[]>>(ENABLED_FEATURES_CTX_KEY);

  return derived([featuresCtx, enabledFeaturesCtx], ([features, enabledFeatures]) =>
    Object.fromEntries(
      Object.entries(features).map(([key, val]) => [
        key,
        { ...val, enabled: enabledFeatures.includes(key as Feature) },
      ]),
    ),
  );
}

export function getAvailableFeatures(environment?: string, user?: OrySchemas.User): Features {
  if (
    (environment && ["development", "localhost"].includes(environment)) ||
    user?.role === "snowfall-admin"
  ) {
    return FEATURES;
  }

  return {
    // To enable a flag in production:
    // [Feature.OFFERS_TIME_WINDOWS]: FEATURES["offers-time-windows"],
  };
}
