import useRuntime from "./useRuntime";

export default function useWorkspace() {
  const {
    runtime,
    setActiveWorkspace,
  } = useRuntime();

  return {
    activeWorkspaceId:
      runtime.activeWorkspaceId,

    workspaces:
      runtime.workspaces || [],

    setActiveWorkspace,
  };
}