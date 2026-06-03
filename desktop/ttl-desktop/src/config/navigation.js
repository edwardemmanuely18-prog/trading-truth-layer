import {
  LayoutDashboard,
  LineChart,
  BrainCircuit,
  ShieldCheck,
  Database,
  Activity,
} from "lucide-react";

export const navigation = [
  {
    id: "dashboard",
    label: "Dashboard",
    route: "/",
    icon: LayoutDashboard,
  },

  {
    id: "markets",
    label: "Markets",
    route: "/markets",
    icon: LineChart,
  },

  {
    id: "execution",
    label: "Execution",
    route: "/execution",
    icon: Activity,
  },

  {
    id: "ai-research",
    label: "AI Research",
    route: "/ai-research",
    icon: BrainCircuit,
  },

  {
    id: "data-engine",
    label: "Data Engine",
    route: "/data-engine",
    icon: Database,
  },

  {
    id: "risk",
    label: "Risk System",
    route: "/risk",
    icon: ShieldCheck,
  },
];