export function normalizeGovernance(usage: any) {
  const used = {
    trades:
      Number(
        usage?.used ??
        usage?.consumed ??
        usage?.usage?.trades ??
        0
      ),

    claims:
      Number(
        usage?.claims_used ??
        usage?.usage?.claims ??
        0
      ),

    members:
      Number(
        usage?.members_used ??
        usage?.usage?.members ??
        0
      ),

    storage_mb:
      Number(
        usage?.storage_used_mb ??
        usage?.usage?.storage_mb ??
        0
      ),
  };

  const limits = {
    trades:
      Number(
        usage?.limit ??
        usage?.limits?.trades ??
        999999999
      ),

    claims:
      Number(
        usage?.claims_limit ??
        usage?.limits?.claims ??
        100
      ),

    members:
      Number(
        usage?.members_limit ??
        usage?.limits?.members ??
        25
      ),

    storage_mb:
      Number(
        usage?.storage_limit_mb ??
        usage?.limits?.storage_mb ??
        10240
      ),
  };

  return {
    used,
    limits,
  };
}