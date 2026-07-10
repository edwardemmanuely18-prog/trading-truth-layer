type Props = {

    authority:string;

    scope:string;

    status:string;

};

export default function AuthorityCard({

    authority,

    scope,

    status,

}:Props){

return(

<div className="rounded-xl border bg-slate-50 p-4">

<div className="text-xs uppercase tracking-wider text-slate-500">

Authority

</div>

<div className="mt-2 text-xl font-bold">

{authority}

</div>

<div className="mt-3 text-sm text-slate-600">

{scope}

</div>

<div className="mt-4">

<span className="rounded-full bg-blue-100 px-3 py-1 text-xs">

{status}

</span>

</div>

</div>

);

}