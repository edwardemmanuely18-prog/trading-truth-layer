import LandingPage from "../pages/public/LandingPage";
import PricingPage from "../pages/public/PricingPage";
import DownloadPage from "../pages/public/DownloadPage";
import PrivacyPage from "../pages/public/PrivacyPage";
import TermsPage from "../pages/public/TermsPage";
import ContactPage from "../pages/public/ContactPage";

export const publicRoutes = [
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