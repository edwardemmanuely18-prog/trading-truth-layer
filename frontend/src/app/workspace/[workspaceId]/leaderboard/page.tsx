import LeaderboardPage from "../../../leaderboard/page";

type Props = {
  params: {
    workspaceId: string;
  };
  searchParams?: Promise<{
    q?: string;
    sort?: string;
    visibility?: string;
    minTrades?: string;
  }>;
};

export default async function WorkspaceLeaderboardWrapper(props: Props) {
  return <LeaderboardPage searchParams={props.searchParams} />;
}