export type OnboardingSchema = {
  id: string;
  type: "onboarding-tokens";
  attributes: {
    companyName: string;
    clientSecret: string;
  };
};

export interface OnboardingModel {
  id: string;
  companyName: string;
  clientSecret: string;
}

export const onboardingParser = {
  toModel: (data: OnboardingSchema): OnboardingModel => {
    return {
      id: data.id,
      companyName: data.attributes.companyName,
      clientSecret: data.attributes.clientSecret,
    };
  },
};
