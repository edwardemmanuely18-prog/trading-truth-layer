"use client";

type Props = {

    timezone:string;

    currency:string;

    language:string;

    dateFormat:string;

    autoRefresh:boolean;

    autoSave:boolean;

    readOnly?: boolean;

    onTimezoneChange?:(v:string)=>void;

    onCurrencyChange?:(v:string)=>void;

    onLanguageChange?:(v:string)=>void;

    onDateFormatChange?:(v:string)=>void;

    onAutoRefreshChange?:(v:boolean)=>void;

    onAutoSaveChange?:(v:boolean)=>void;

};

export default function WorkspacePreferencesCard({

    timezone,

    currency,

    language,

    dateFormat,

    autoRefresh,

    autoSave,

    readOnly=false,

    onTimezoneChange,

    onCurrencyChange,

    onLanguageChange,

    onDateFormatChange,

    onAutoRefreshChange,

    onAutoSaveChange,

}:Props){

    return(

        <div className="rounded-3xl border bg-white p-6 shadow-sm">

            <h2 className="text-2xl font-semibold">

                Workspace Preferences

            </h2>

            <p className="mt-2 text-sm text-slate-500">

                Default workspace behaviour and regional
                configuration.

            </p>

            <div className="mt-6 grid gap-6 md:grid-cols-2">

                <Field
                    label="Timezone"
                    value={timezone}
                    readOnly={readOnly}
                    onChange={onTimezoneChange}
                />

                <Field
                    label="Currency"
                    value={currency}
                    readOnly={readOnly}
                    onChange={onCurrencyChange}
                />

                <Field
                    label="Language"
                    value={language}
                    readOnly={readOnly}
                    onChange={onLanguageChange}
                />

                <Field
                    label="Date Format"
                    value={dateFormat}
                    readOnly={readOnly}
                    onChange={onDateFormatChange}
                />

            </div>

            <div className="mt-8 space-y-4">

                <Toggle

                    label="Automatic Refresh"

                    checked={autoRefresh}

                    readOnly={readOnly}

                    onChange={onAutoRefreshChange}

                />

                <Toggle

                    label="Automatic Save"

                    checked={autoSave}

                    readOnly={readOnly}

                    onChange={onAutoSaveChange}

                />

            </div>

        </div>

    );

}

function Field({

    label,

    value,

    readOnly,

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

function Toggle({

    label,

    checked,

    readOnly = false,

    onChange,

}:{

    label:string;

    checked:boolean;

    readOnly?:boolean;

    onChange?:(v:boolean)=>void;

}){

    return(

        <label className="flex items-center justify-between rounded-xl border p-4">

            <span>

                {label}

            </span>

            <input

                type="checkbox"

                checked={checked}

                disabled={readOnly}

                onChange={(e)=>

                    onChange?.(

                        e.target.checked

                    )

                }

            />

        </label>

    );

}