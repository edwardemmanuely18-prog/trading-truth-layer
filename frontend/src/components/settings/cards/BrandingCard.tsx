"use client";

type Props = {

    organization:string;

    website:string;

    logo:string;

    primaryColor:string;

    accentColor:string;

    reportFooter:string;

    disclaimer:string;

    readOnly?: boolean;

    onOrganizationChange?:(v:string)=>void;

    onWebsiteChange?:(v:string)=>void;

    onLogoChange?:(v:string)=>void;

    onPrimaryColorChange?:(v:string)=>void;

    onAccentColorChange?:(v:string)=>void;

    onFooterChange?:(v:string)=>void;

    onDisclaimerChange?:(v:string)=>void;

};

export default function BrandingCard({

    organization,

    website,

    logo,

    primaryColor,

    accentColor,

    reportFooter,

    disclaimer,

    readOnly = false,

    onOrganizationChange,

    onWebsiteChange,

    onLogoChange,

    onPrimaryColorChange,

    onAccentColorChange,

    onFooterChange,

    onDisclaimerChange,

}:Props){

    return(

        <div className="rounded-3xl border bg-white p-6 shadow-sm">

            <h2 className="text-2xl font-semibold">

                Workspace Branding

            </h2>

            <p className="mt-2 text-sm text-slate-500">

                Configure the visual identity used across
                reports, public pages and exported evidence.

            </p>

            <div className="mt-6 grid gap-6">

                <Input

                    label="Organization"

                    value={organization}

                    readOnly={readOnly}

                    onChange={onOrganizationChange}

                />

                <Input

                    label="Website"

                    value={website}

                    readOnly={readOnly}

                    onChange={onWebsiteChange}

                />

                <div className="md:col-span-2">
                    <div className="mb-2 text-sm font-medium">
                        Platform Logo
                    </div>

                    <div className="flex h-64 items-center justify-center rounded-xl border bg-white p-6">
                        <img
                            src={logo}
                            alt="Trading Truth Layer"
                            className="max-h-full max-w-full object-contain"
                        />
                    </div>
                </div>

            </div>

            <div className="mt-6">

                <label className="text-sm font-medium">

                    Report Footer

                </label>

                <textarea

                    rows={3}

                    readOnly={readOnly}

                    disabled={readOnly}

                    className="mt-2 w-full rounded-xl border bg-slate-50 px-4 py-3"

                    value={reportFooter}

                    onChange={(e)=>

                        onFooterChange?.(

                            e.target.value

                        )

                    }

                />

            </div>

            <div className="mt-6">

                <label className="text-sm font-medium">

                    Report Disclaimer

                </label>

                <textarea

                    rows={4}

                    className="mt-2 w-full rounded-xl border bg-slate-50 px-4 py-3"

                    value={disclaimer}

                    readOnly={readOnly}

                    disabled={readOnly}

                    onChange={(e)=>

                        onDisclaimerChange?.(

                            e.target.value

                        )

                    }

                />

            </div>

        </div>

    );

}

function Input({

    label,

    value,

    readOnly = false,

    onChange,

}:{

    label:string;

    value:string;

    readOnly?:boolean;

    onChange?:(v:string)=>void;

}){

    return(

        <div>

            <div className="mb-2 text-sm font-medium">

                {label}

            </div>

            <input

                className="w-full rounded-xl border bg-slate-50 px-4 py-3"

                value={value}

                readOnly={readOnly}

                disabled={readOnly}

                onChange={(e)=>

                    onChange?.(

                        e.target.value

                    )

                }

            />

        </div>

    );

}