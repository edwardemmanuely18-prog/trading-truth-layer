"use client";

type Props = {

    timezone:string;

    currency:string;

    language:string;

    dateFormat:string;

    autoRefresh:boolean;

    autoSave:boolean;

    onTimezoneChange:(v:string)=>void;

    onCurrencyChange:(v:string)=>void;

    onLanguageChange:(v:string)=>void;

    onDateFormatChange:(v:string)=>void;

    onAutoRefreshChange:(v:boolean)=>void;

    onAutoSaveChange:(v:boolean)=>void;

};

export default function WorkspacePreferencesCard({

    timezone,

    currency,

    language,

    dateFormat,

    autoRefresh,

    autoSave,

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
                    onChange={onTimezoneChange}
                />

                <Field
                    label="Currency"
                    value={currency}
                    onChange={onCurrencyChange}
                />

                <Field
                    label="Language"
                    value={language}
                    onChange={onLanguageChange}
                />

                <Field
                    label="Date Format"
                    value={dateFormat}
                    onChange={onDateFormatChange}
                />

            </div>

            <div className="mt-8 space-y-4">

                <Toggle

                    label="Automatic Refresh"

                    checked={autoRefresh}

                    onChange={onAutoRefreshChange}

                />

                <Toggle

                    label="Automatic Save"

                    checked={autoSave}

                    onChange={onAutoSaveChange}

                />

            </div>

        </div>

    );

}

function Field({

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

                onChange={(e)=>onChange(e.target.value)}

            />

        </div>

    );

}

function Toggle({

    label,

    checked,

    onChange,

}:{

    label:string;

    checked:boolean;

    onChange:(v:boolean)=>void;

}){

    return(

        <label className="flex items-center justify-between rounded-xl border p-4">

            <span>

                {label}

            </span>

            <input

                type="checkbox"

                checked={checked}

                onChange={(e)=>onChange(e.target.checked)}

            />

        </label>

    );

}