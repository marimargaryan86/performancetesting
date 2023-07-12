import type { ConversionModel } from "models/conversion";
import type { ConversionSchema } from "../schemas/conversion";
import { parseTransactionSchema } from "./transaction";
import type { TransactionSchema } from "../schemas/transaction";

export function parseConversionSchema(
  conversion: ConversionSchema,
  transactions: TransactionSchema[] = [],
): ConversionModel {
  const transaction = transactions.find(
    (item) => item.id === conversion.relationships?.transactions.data.id,
  );

  return {
    id: conversion.id,
    buyAmount: conversion.attributes.buyAmount,
    createdAt: conversion.attributes.createdAt
      ? new Date(conversion.attributes.createdAt)
      : undefined,
    executedRate: conversion.attributes.executedRate,
    fxDelta: conversion.attributes.fxDelta ?? undefined,
    fxStatus: conversion.attributes.fxStatus,
    sellAmount: conversion.attributes.sellAmount ?? undefined,
    settledAt: conversion.attributes.settledAt
      ? new Date(conversion.attributes.settledAt)
      : undefined,
    transaction: transaction ? parseTransactionSchema(transaction, []) : undefined,
  };
}
