"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

interface Props {
    workspaceId: number;
    initialValue?: string;
}

export default function ProfileClaimSearch({
    workspaceId,
    initialValue = "",
}: Props) {

    const router = useRouter();

    const [value, setValue] = useState(
        initialValue,
    );

    function handleSearch(
        searchValue: string,
    ) {

        const query =
            searchValue.trim();

        if (!query) {

            router.push(
                `/profile/${workspaceId}`,
            );

            return;

        }

        router.push(
            `/profile/${workspaceId}?q=${encodeURIComponent(
                query,
            )}`,
        );

    }

    return (

        <input

            type="text"

            value={value}

            placeholder="Search by claim name, claim ID or claim hash..."

            onChange={(e) => {

                const nextValue =
                    e.target.value;

                setValue(
                    nextValue,
                );

                handleSearch(
                    nextValue,
                );

            }}

            className="w-full rounded-xl border border-slate-200 px-4 py-3 text-sm"

        />

    );

}