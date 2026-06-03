import DashboardPage from "../../pages/dashboard/DashboardPage";
import MarketsPage from "../../pages/markets/MarketsPage";
import ExecutionPage from "../../pages/execution/ExecutionPage";
import AIResearchPage from "../../pages/ai-research/AIResearchPage";
import DataEnginePage from "../../pages/data-engine/DataEnginePage";
import RiskPage from "../../pages/risk/RiskPage";

/* PUBLIC WEBSITE */
import LandingPage from "../../pages/public/LandingPage";
import PricingPage from "../../pages/public/PricingPage";
import DownloadPage from "../../pages/public/DownloadPage";
import PrivacyPage from "../../pages/public/PrivacyPage";
import TermsPage from "../../pages/public/TermsPage";
import ContactPage from "../../pages/public/ContactPage";

export const appRoutes = [
  /* =========================
     DESKTOP APP ROUTES
  ========================= */

  {
    path: "/",
    element: <DashboardPage />,
  },

  {
    path: "/markets",
    element: <MarketsPage />,
  },

  {
    path: "/execution",
    element: <ExecutionPage />,
  },

  {
    path: "/ai-research",
    element: <AIResearchPage />,
  },

  {
    path: "/data-engine",
    element: <DataEnginePage />,
  },

  {
    path: "/risk",
    element: <RiskPage />,
  },

  /* =========================
     PUBLIC WEBSITE PAGES
  ========================= */

  {
    path: "/welcome",
    element: <LandingPage />,
  },

  {
    path: "/pricing",
    element: <PricingPage />,
  },

  {
    path: "/download",
    element: <DownloadPage />,
  },

  {
    path: "/privacy-policy",
    element: <PrivacyPage />,
  },

  {
    path: "/terms",
    element: <TermsPage />,
  },

  {
    path: "/contact",
    element: <ContactPage />,
  },
];