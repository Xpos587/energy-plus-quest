/** Optional hint only; browsers without this API keep the normal network path. */
export function constrainedConnection() {
  const connection = (
    navigator as Navigator & {
      connection?: {
        saveData?: boolean;
        effectiveType?: string;
        downlink?: number;
      };
    }
  ).connection;
  return Boolean(
    connection?.saveData ||
      /^(slow-)?[23]g$/.test(connection?.effectiveType ?? "") ||
      (connection?.downlink !== undefined && connection.downlink < 1),
  );
}

/** Observed transfers also work in browsers without Network Information. */
export function observedSlowTransfer() {
  if (typeof performance?.getEntriesByType !== "function") return false;
  return performance.getEntriesByType("resource").some((entry) => {
    const transfer = entry as PerformanceResourceTiming;
    return (
      transfer.transferSize > 0 &&
      transfer.encodedBodySize > 20_000 &&
      transfer.duration > 1_500 &&
      transfer.encodedBodySize / (transfer.duration / 1_000) < 125_000
    );
  });
}
