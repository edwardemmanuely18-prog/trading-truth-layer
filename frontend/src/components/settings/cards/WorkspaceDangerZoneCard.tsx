"use client";

type Props={

    onExport:()=>void;

    onArchive:()=>void;

    onTransfer:()=>void;

    onDelete:()=>void;

};

function Action({

    title,

    description,

    button,

    variant,

    onClick,

}:{

    title:string;

    description:string;

    button:string;

    variant:"default"|"danger";

    onClick:()=>void;

}){

    return(

        <div className="flex items-center justify-between rounded-xl border p-5">

            <div>

                <div className="font-semibold">

                    {title}

                </div>

                <div className="mt-1 text-sm text-slate-500">

                    {description}

                </div>

            </div>

            <button

                onClick={onClick}

                className={`rounded-xl px-5 py-2 text-white ${
                    variant==="danger"
                    ? "bg-red-600 hover:bg-red-700"
                    : "bg-slate-900 hover:bg-slate-800"
                }`}

            >

                {button}

            </button>

        </div>

    );

}

export default function WorkspaceDangerZoneCard({

    onExport,

    onArchive,

    onTransfer,

    onDelete,

}:Props){

    return(

        <div className="rounded-3xl border border-red-300 bg-white p-6 shadow-sm">

            <h2 className="text-2xl font-semibold text-red-700">

                Danger Zone

            </h2>

            <p className="mt-2 text-sm text-slate-500">

                High-impact workspace operations.
                These actions may be irreversible.

            </p>

            <div className="mt-6 space-y-4">

                <Action

                    title="Export Workspace"

                    description="Export the complete workspace."

                    button="Export"

                    variant="default"

                    onClick={onExport}

                />

                <Action

                    title="Archive Workspace"

                    description="Archive without deleting."

                    button="Archive"

                    variant="default"

                    onClick={onArchive}

                />

                <Action

                    title="Transfer Ownership"

                    description="Transfer workspace ownership."

                    button="Transfer"

                    variant="default"

                    onClick={onTransfer}

                />

                <Action

                    title="Delete Workspace"

                    description="Permanent removal of all workspace data."

                    button="Delete"

                    variant="danger"

                    onClick={onDelete}

                />

            </div>

        </div>

    );

}