import fs from "fs/promises";

export async function readFile<T>(path: string): Promise<T> {
  const file = await fs.readFile(path, "utf-8");

  return JSON.parse(file);
}

export function writeFile(path: string, data: string): Promise<void> {
  return fs.writeFile(path, data, "utf-8");
}
