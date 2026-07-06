"use client";

type Props = {

    verificationExposure: string;

    externalVerification: string;

    apiAccess: string;

    brokerConnections: string;

    webhooks: string;

    trustNetwork: string;

};

function Item({

    title,

    value,

}:{

    title:string;

    value:string;

}){

    return(

        <div className="rounded-xl border bg-slate-50 p-4">

            <div className="text-sm text-slate-500">

                {title}

            </div>

            <div className="mt-2 text-lg font-semibold">

                {value}

            </div>

        </div>

    );

}

export default function PlatformReadinessCard({

    verificationExposure,

    externalVerification,

    apiAccess,

    brokerConnections,

    webhooks,

    trustNetwork,

}:Props){

    return(

        <div className="rounded-3xl border bg-white p-6 shadow-sm">

            <h2 className="text-2xl font-semibold">

                Platform Readiness

            </h2>

            <p className="mt-2 text-sm text-slate-500">

                Operational posture of this workspace
                across verification infrastructure.

            </p>

            <div className="mt-6 grid gap-4 md:grid-cols-2">

                <Item
                    title="Verification Exposure"
                    value={verificationExposure}
                />

                <Item
                    title="External Verification"
                    value={externalVerification}
                />

                <Item
                    title="API Access"
                    value={apiAccess}
                />

                <Item
                    title="Broker Connections"
                    value={brokerConnections}
                />

                <Item
                    title="Webhook Infrastructure"
                    value={webhooks}
                />

                <Item
                    title="Trust Network"
                    value={trustNetwork}
                />

            </div>

        </div>

    );

}