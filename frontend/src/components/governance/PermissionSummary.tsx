type Props={

role:string;

};

const MATRIX={

owner:[
"Identity",
"Billing",
"Verification",
"Workspace",
"Trust Layer"
],

operator:[
"Claims",
"Evidence",
"Reports"
],

auditor:[
"Review",
"Verification",
"Evidence"
],

member:[
"Claims"
]

} as const;

export default function PermissionSummary({

role

}:Props){

const permissions=

MATRIX[
(role||"member").toLowerCase() as keyof typeof MATRIX
]??MATRIX.member;

return(

<div className="rounded-xl border bg-white p-4">

<div className="text-xs uppercase tracking-wide text-slate-500">

Permissions

</div>

<div className="mt-3 flex flex-wrap gap-2">

{permissions.map(permission=>(

<span

key={permission}

className="rounded-full bg-slate-100 px-3 py-1 text-xs"

>

{permission}

</span>

))}

</div>

</div>

);

}