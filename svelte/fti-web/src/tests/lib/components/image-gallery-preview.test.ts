import "@testing-library/jest-dom/vitest";
import { describe, it, expect } from "vitest";
import { render, fireEvent, screen } from "@testing-library/svelte";
import ImageGalleryPreview from "$lib/components/image-gallery-preview.svelte";
import { MOCK_HOTEL_INFO } from "../../../routes/hotels/+page.svelte";

describe("ImageGalleryPreview Component", () => {
  const hotelInfo = MOCK_HOTEL_INFO;

  it("should render with initial selected image", () => {
    const { getByAltText } = render(ImageGalleryPreview, { hotelInfo });

    const image = getByAltText("Selected Hotel Image");
    expect(image).toBeInTheDocument();
    expect(image).toHaveAttribute("src", "/images/hotel-gallery/1.jpg");
  });

  // TODO: Update test case after component is updated
  it.skip("renders thumbnails and reacts to click", async () => {
    const { getAllByRole, getByText } = render(ImageGalleryPreview, { hotelInfo });
    const thumbnails = getAllByRole("button");
    expect(thumbnails.length).toBeGreaterThan(4);
    screen.debug();
    await fireEvent.click(thumbnails[4]);

    expect(getByText("View Gallery (+5)")).toBeInTheDocument();
  });

  it.skip("shows the correct image src when using the arrow buttons");
  it.skip("shows the correct image src when clicking the image thumbnail");
});
