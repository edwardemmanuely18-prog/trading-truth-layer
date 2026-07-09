"use client";

import UpgradeRequired
from "@/components/entitlement/UpgradeRequired";

type Props={

    enabled:boolean;

    children:React.ReactNode;

    feature:string;

};

export default function FeatureGate({

    enabled,

    children,

    feature,

}:Props){

    if(enabled){

        return<>{children}</>;

    }

    return(

        <UpgradeRequired

            feature={feature}

        />

    );

}