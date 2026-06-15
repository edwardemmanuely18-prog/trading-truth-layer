"use client";

import { useEffect } from "react";
import { useParams, useRouter }
from "next/navigation";

export default function ImportRedirect() {
  const router = useRouter();
  const params = useParams();

  useEffect(() => {
    router.replace(
      `/workspace/${params.workspaceId}/import-center`
    );
  }, [router, params]);

  return null;
}