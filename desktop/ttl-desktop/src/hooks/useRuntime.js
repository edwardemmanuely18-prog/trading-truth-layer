import { useRuntimeContext } from "../providers/RuntimeProvider";

export default function useRuntime() {
  return useRuntimeContext();
}