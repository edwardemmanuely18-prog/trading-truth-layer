"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

type Props = {
    href: string;
};

export default function VerifyButton(
    { href }: Props,
) {

    const router = useRouter();

    const [loading, setLoading] =
        useState(false);

    return (

        <button
            disabled={loading}
            onClick={() => {

                setLoading(true);

                router.push(href);

            }}
            className="
                rounded-lg
                border
                border-slate-300
                px-3
                py-2
                text-xs
                font-medium
                hover:bg-slate-50
                disabled:opacity-60
            "
        >

            {loading
                ? "Verifying..."
                : "Verify"}

        </button>

    );

}