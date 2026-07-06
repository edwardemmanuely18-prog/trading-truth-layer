"use client";

type Props = {

    organization:string;

    website:string;

    logo:string;

    primaryColor:string;

    accentColor:string;

    reportFooter:string;

    disclaimer:string;

    onOrganizationChange:(v:string)=>void;

    onWebsiteChange:(v:string)=>void;

    onLogoChange:(v:string)=>void;

    onPrimaryColorChange:(v:string)=>void;

    onAccentColorChange:(v:string)=>void;

    onFooterChange:(v:string)=>void;

    onDisclaimerChange:(v:string)=>void;

};

export default function BrandingCard({

    organization,

    website,

    logo,

    primaryColor,

    accentColor,

    reportFooter,

    disclaimer,

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

            <div className="mt-6 grid gap-5 md:grid-cols-2">

                <Input

                    label="Organization"

                    value={organization}

                    onChange={onOrganizationChange}

                />

                <Input

                    label="Website"

                    value={website}

                    onChange={onWebsiteChange}

                />

                <Input

                    label="Logo URL"

                    value={logo}

                    onChange={onLogoChange}

                />

                <Input

                    label="Primary Color"

                    value={primaryColor}

                    onChange={onPrimaryColorChange}

                />

                <Input

                    label="Accent Color"

                    value={accentColor}

                    onChange={onAccentColorChange}

                />

            </div>

            <div className="mt-6">

                <label className="text-sm font-medium">

                    Report Footer

                </label>

                <textarea

                    rows={3}

                    className="mt-2 w-full rounded-xl border px-4 py-3"

                    value={reportFooter}

                    onChange={(e)=>

                        onFooterChange(

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

                    className="mt-2 w-full rounded-xl border px-4 py-3"

                    value={disclaimer}

                    onChange={(e)=>

                        onDisclaimerChange(

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

    onChange,

}:{

    label:string;

    value:string;

    onChange:(v:string)=>void;

}){

    return(

        <div>

            <div className="mb-2 text-sm font-medium">

                {label}

            </div>

            <input

                className="w-full rounded-xl border px-4 py-3"

                value={value}

                onChange={(e)=>

                    onChange(

                        e.target.value

                    )

                }

            />

        </div>

    );

}