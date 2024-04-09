import { promises as fs } from "fs";

export async function GET(): Promise<Response> {
  const imagesDirectory = "static/images/hotel-gallery";
  const files = await fs.readdir(imagesDirectory);

  const imagePaths = files.map((file) => `/images/hotel-gallery/${file}`);

  return new Response(JSON.stringify(imagePaths), {
    status: 200,
    headers: {
      "Content-Type": "application/json",
    },
  });
}
