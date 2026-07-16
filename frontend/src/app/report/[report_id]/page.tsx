// frontend/src/app/report/[report_id]/page.tsx

import { notFound } from "next/navigation";
import { headers } from "next/headers";

type Props = {
    params: Promise<{
        report_id: string;
    }>;
};

export const dynamic = "force-dynamic";

export default async function ReportPage(
    { params }: Props,
) {
    const { report_id } = await params;

    const host = (await headers()).get("host");

    const protocol =
        host?.includes("localhost")
            ? "http"
            : "https";

    const baseUrl = `${protocol}://${host}`;

    const response = await fetch(
        `${baseUrl}/api/report/${report_id}`,
        {
            cache: "no-store",
        },
    );

    if (!response.ok) {
        notFound();
    }

    const html = await response.text();

    return (
        <div
            dangerouslySetInnerHTML={{
                __html: html,
            }}
        />
    );
}