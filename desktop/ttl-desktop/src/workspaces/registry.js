import {
  LayoutDashboard,
  BarChart3,
  BrainCircuit,
  Shield,
  Database,
  Activity,
} from "lucide-react";

export const workspaceRegistry = [
  {
    id: "dashboard",
    title: "Dashboard",
    icon: LayoutDashboard,
    route: "/",
  },
  {
    id: "markets",
    title: "Markets",
    icon: BarChart3,
    route: "/markets",
  },
  {
    id: "execution",
    title: "Execution",
    icon: Activity,
    route: "/execution",
  },
  {
    id: "ai-research",
    title: "AI Research",
    icon: BrainCircuit,
    route: "/ai-research",
  },
  {
    id: "data-engine",
    title: "Data Engine",
    icon: Database,
    route: "/data-engine",
  },
  {
    id: "risk",
    title: "Risk System",
    icon: Shield,
    route: "/risk",
  },
];