import { api } from "../../../lib/api";
import PublicClaimsClient from "./PublicClaimsClient";

export const revalidate = 60;

export default async function PublicClaimsPage() {
  let claims: any[] = [];

  try {
    claims = await api.getGlobalPublicClaims();
  } catch (e) {
    console.error("Failed to load public claims", e);
  }

  return <PublicClaimsClient initialClaims={claims} />;
}