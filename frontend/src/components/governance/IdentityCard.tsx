import { WorkspaceMember } from "../../lib/api";

type Props = {
  member: WorkspaceMember;
};

function initials(name?: string) {
  if (!name) return "?";

  return name
    .split(" ")
    .map(x => x[0])
    .join("")
    .substring(0, 2)
    .toUpperCase();
}

export default function IdentityCard({
  member,
}: Props) {
  return (
    <div className="max-w-[340px] rounded-2xl border bg-white p-5">

      <div className="flex items-start gap-4">

        <div className="flex h-14 w-14 items-center justify-center rounded-full bg-slate-900 text-xl font-bold text-white">

          {initials(member.name)}

        </div>

        <div>

          <div className="text-lg font-semibold">

            {member.name}

          </div>

          <div className="text-sm text-slate-500">

            {member.email}

          </div>

          <div className="mt-2 inline-flex rounded-full bg-slate-100 px-3 py-1 text-xs">

            User #{member.user_id}

          </div>

        </div>

      </div>

    </div>
  );
}