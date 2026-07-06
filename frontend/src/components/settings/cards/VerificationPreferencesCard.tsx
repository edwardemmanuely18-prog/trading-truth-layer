"use client";

type ToggleProps={

    label:string;

    description:string;

    enabled:boolean;

    onChange:(v:boolean)=>void;

};

function Toggle({

    label,

    description,

    enabled,

    onChange,

}:ToggleProps){

    return(

        <div className="rounded-xl border p-5">

            <div className="flex items-center justify-between">

                <div>

                    <div className="font-semibold">

                        {label}

                    </div>

                    <div className="mt-1 text-sm text-slate-500">

                        {description}

                    </div>

                </div>

                <input

                    type="checkbox"

                    checked={enabled}

                    onChange={(e)=>

                        onChange(

                            e.target.checked

                        )

                    }

                />

            </div>

        </div>

    );

}

type Props={

    publicVerification:boolean;

    verificationRoutes:boolean;

    trustScore:boolean;

    qrCodes:boolean;

    jsonEvidence:boolean;

    pdfEvidence:boolean;

    zipEvidence:boolean;

    autoLock:boolean;

    autoPublish:boolean;

    onPublicVerification:(v:boolean)=>void;

    onVerificationRoutes:(v:boolean)=>void;

    onTrustScore:(v:boolean)=>void;

    onQrCodes:(v:boolean)=>void;

    onJsonEvidence:(v:boolean)=>void;

    onPdfEvidence:(v:boolean)=>void;

    onZipEvidence:(v:boolean)=>void;

    onAutoLock:(v:boolean)=>void;

    onAutoPublish:(v:boolean)=>void;

};

export default function VerificationPreferencesCard({

    publicVerification,

    verificationRoutes,

    trustScore,

    qrCodes,

    jsonEvidence,

    pdfEvidence,

    zipEvidence,

    autoLock,

    autoPublish,

    onPublicVerification,

    onVerificationRoutes,

    onTrustScore,

    onQrCodes,

    onJsonEvidence,

    onPdfEvidence,

    onZipEvidence,

    onAutoLock,

    onAutoPublish,

}:Props){

    return(

        <div className="rounded-3xl border bg-white p-6 shadow-sm">

            <h2 className="text-2xl font-semibold">

                Verification Preferences

            </h2>

            <p className="mt-2 text-sm text-slate-500">

                Configure verification behaviour for
                the workspace.

            </p>

            <div className="mt-6 grid gap-4">

                <Toggle

                    label="Public Verification"

                    description="Expose public verification pages."

                    enabled={publicVerification}

                    onChange={onPublicVerification}

                />

                <Toggle

                    label="Verification Routes"

                    description="Enable verification URLs."

                    enabled={verificationRoutes}

                    onChange={onVerificationRoutes}

                />

                <Toggle

                    label="Trust Score"

                    description="Display institutional trust score."

                    enabled={trustScore}

                    onChange={onTrustScore}

                />

                <Toggle

                    label="QR Verification"

                    description="Generate QR verification codes."

                    enabled={qrCodes}

                    onChange={onQrCodes}

                />

                <Toggle

                    label="JSON Evidence"

                    description="Allow JSON evidence exports."

                    enabled={jsonEvidence}

                    onChange={onJsonEvidence}

                />

                <Toggle

                    label="PDF Evidence"

                    description="Allow PDF evidence exports."

                    enabled={pdfEvidence}

                    onChange={onPdfEvidence}

                />

                <Toggle

                    label="ZIP Evidence"

                    description="Allow ZIP evidence exports."

                    enabled={zipEvidence}

                    onChange={onZipEvidence}

                />

                <Toggle

                    label="Automatic Lock"

                    description="Automatically lock completed claims."

                    enabled={autoLock}

                    onChange={onAutoLock}

                />

                <Toggle

                    label="Automatic Publish"

                    description="Automatically publish verified claims."

                    enabled={autoPublish}

                    onChange={onAutoPublish}

                />

            </div>

        </div>

    );

}