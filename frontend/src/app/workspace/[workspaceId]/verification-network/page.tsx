"use client";

import {

    useEffect,

    useState,

} from "react";

import {

    useParams,

} from "next/navigation";

import Navbar from "../../../../components/Navbar";

import {

    VerificationAnalytics,

    getVerificationAnalytics,

} from "../../../../lib/api";

import ExecutiveOverview from "../../../../components/verification-network/ExecutiveOverview";

import TrustCoverage from "../../../../components/verification-network/TrustCoverage";

import LifecyclePipeline from "../../../../components/verification-network/LifecyclePipeline";

import BrokerNetwork from "../../../../components/verification-network/BrokerNetwork";

import IntegrityOverview from "../../../../components/verification-network/IntegrityOverview";

import PublicNetwork from "../../../../components/verification-network/PublicNetwork";

import ClaimRegistry from "../../../../components/verification-network/ClaimRegistry";

export default function VerificationNetworkPage() {

    const params = useParams();

    const workspaceId =

        Number(

            params.workspaceId,

        );

    const [

        data,

        setData,

    ] =

        useState<VerificationAnalytics | null>(

            null,

        );

    const [

        loading,

        setLoading,

    ] =

        useState(

            true,

        );

    useEffect(() => {

        async function load() {

            try {

                const response =

                    await getVerificationAnalytics(

                        workspaceId,

                    );

                setData(

                    response,

                );

            }

            catch (

                err

            ) {

                console.error(

                    err,

                );

            }

            finally {

                setLoading(

                    false,

                );

            }

        }

        if (

            !Number.isNaN(

                workspaceId,

            )

        ) {

            load();

        }

    }, [

        workspaceId,

    ]);

    return (

        <div className="min-h-screen bg-slate-50">

            <Navbar/>

            <div className="mx-auto max-w-7xl space-y-8 px-6 py-8">

                {loading && (

                    <div className="rounded-2xl border bg-white p-8 text-center">

                        Loading Verification Network...

                    </div>

                )}

                {!loading && data && (

                    <>

                        <ExecutiveOverview

                            data={data}

                        />

                        <TrustCoverage

                            data={data}

                        />

                        <LifecyclePipeline

                            data={data}

                        />

                        <BrokerNetwork

                            data={data}

                        />

                        <IntegrityOverview

                            data={data}

                        />

                        <PublicNetwork

                            data={data}

                        />

                        <ClaimRegistry

                            data={data}

                        />

                    </>

                )}

            </div>

        </div>

    );

}