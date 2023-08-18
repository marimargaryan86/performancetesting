export function getRandomId(prefix?: string): string {
  return `${prefix ? `${prefix}-` : "a-"}${Math.random().toString(32)}`;
}

const alpha = "abcdefghijklmnopqrstuvwxyz";
const alphaUpper = alpha.toUpperCase();
const num = "0123456789";
const alphaNum = `${alpha}${alphaUpper}${num}`;

export function getRandomAlphaNumericString(length: number): string {
  return Array<string>(length)
    .fill("")
    .map(() => alphaNum[Math.floor(Math.random() * alphaNum.length)])
    .join();
}
