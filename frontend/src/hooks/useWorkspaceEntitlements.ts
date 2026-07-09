"use client";

import { useEffect, useState } from "react";

import {
    getWorkspaceEntitlements,
} from "@/lib/api";

import type {
    WorkspaceEntitlements,
} from "@/lib/entitlements";

export function useWorkspaceEntitlements(
    workspaceId: number,
) {
    const [
        entitlements,
        setEntitlements,
    ] = useState<WorkspaceEntitlements | null>(
        null,
    );

    const [
        loading,
        setLoading,
    ] = useState(true);

    const [
        error,
        setError,
    ] = useState<string | null>(
        null,
    );

    useEffect(() => {

        let mounted = true;

        async function load() {

            try {

                setLoading(true);

                const result =
                    await getWorkspaceEntitlements(
                        workspaceId,
                    );

                if (!mounted) {
                    return;
                }

                setEntitlements(
                    result,
                );

                setError(
                    null,
                );

            } catch (err: any) {

                if (!mounted) {
                    return;
                }

                setError(
                    err?.message ??
                    "Unable to load workspace entitlements.",
                );

            } finally {

                if (mounted) {

                    setLoading(
                        false,
                    );

                }

            }

        }

        if (workspaceId > 0) {

            void load();

        }

        return () => {

            mounted = false;

        };

    }, [
        workspaceId,
    ]);

    return {

        entitlements,

        loading,

        error,

    };

}