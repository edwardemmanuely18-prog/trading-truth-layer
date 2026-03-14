import VerificationBadgeCard from "../../../components/VerificationBadgeCard";
import { api } from "../../../lib/api";

type PageProps = {
  params: Promise<{
    claimHash: string;
  }>;
};

export default async function EmbedClaimPage({ params }: PageProps) {
  const resolvedParams = await params;
  const claimHash = resolvedParams.claimHash;

  const claim = await api.getPublicClaimByHash(claimHash);

  return (
    <main className="min-h-screen bg-transparent p-4">
      <div className="flex min-h-screen items-center justify-center">
        <VerificationBadgeCard
          name={claim.name}
          claimSchemaId={claim.claim_schema_id}
          verificationStatus={claim.verification_status}
          integrityStatus={claim.integrity_status}
          tradeCount={claim.trade_count}
          netPnl={claim.net_pnl}
          profitFactor={claim.profit_factor}
          winRate={claim.win_rate}
          claimHash={claim.claim_hash}
          verifyHref={`/verify/${claim.claim_hash}`}
        />
      </div>
    </main>
  );
}
