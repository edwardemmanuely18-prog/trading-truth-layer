import { notFound } from "next/navigation";

type Props = {
    params: Promise<{
        report_id: string;
    }>;
};

export const dynamic = "force-dynamic";

export default async function ReportDownloadPage(
    { params }: Props,
) {
    const { report_id } = await params;

    const backendBase = (
        process.env.NEXT_PUBLIC_BACKEND_URL ||
        "http://127.0.0.1:8001"
    ).replace(/\/+$/, "");

    const response = await fetch(
        `${backendBase}/report/${report_id}/download`,
        {
            cache: "no-store",
        },
    );

    if (!response.ok) {
        notFound();
    }

    const pdfBuffer = await response.arrayBuffer();

    return new Response(
        pdfBuffer,
        {
            headers: {
                "Content-Type": "application/pdf",
                "Content-Disposition": `inline; filename="${report_id}.pdf"`,
            },
        },
    );
}