import type { ConversionModel } from "models/conversion";
import type { ConversionSchema } from "../schemas/conversion";
import { parseTransaction } from "./transaction";
import type { TransactionSchema } from "../schemas/transaction";

export function parseConversion(
  conversion: ConversionSchema,
  transactions: TransactionSchema[] = [],
): ConversionModel {
  const transaction = transactions.find(
    (item) => item.id === conversion.relationships?.transactions.data.id,
  );

  return {
    id: conversion.id,
    buyAmount: conversion.attributes.buyAmount,
    createdAt: new Date(conversion.attributes.createdAt),
    executedRate: conversion.attributes.executedRate,
    fxDelta: conversion.attributes.fxDelta,
    fxStatus: conversion.attributes.fxStatus,
    sellAmount: conversion.attributes.sellAmount,
    settledAt: new Date(conversion.attributes.settledAt),
    transaction: transaction ? parseTransaction(transaction, []) : undefined,
  };
}
