import { notFound } from "next/navigation";

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

    const backendBase = (
        process.env.NEXT_PUBLIC_BACKEND_URL ||
        "http://127.0.0.1:8001"
    ).replace(/\/+$/, "");

    const response = await fetch(
        `${backendBase}/report/${report_id}`,
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