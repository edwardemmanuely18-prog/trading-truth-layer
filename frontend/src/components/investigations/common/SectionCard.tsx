"use client";

import { ReactNode } from "react";

interface Props {

    title: string;

    subtitle?: string;

    children: ReactNode;

}

export default function SectionCard({

    title,

    subtitle,

    children,

}: Props) {

    return (

        <div
            className="
                rounded-xl
                border
                bg-white
                dark:bg-neutral-900
                shadow-sm
                mb-6
            "
        >

            <div
                className="
                    border-b
                    px-6
                    py-4
                "
            >

                <h2
                    className="
                        text-lg
                        font-semibold
                    "
                >
                    {title}
                </h2>

                {subtitle && (

                    <p
                        className="
                            text-sm
                            text-gray-500
                            mt-1
                        "
                    >
                        {subtitle}
                    </p>

                )}

            </div>

            <div className="p-6">

                {children}

            </div>

        </div>

    );

}