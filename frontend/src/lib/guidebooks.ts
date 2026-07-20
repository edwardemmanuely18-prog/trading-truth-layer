const BACKEND_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ??
  "http://localhost:8001";


export const GUIDEBOOKS = [
  {
    volume: "VOLUME I",

    title:
      "Institutional Trading Trust Infrastructure",

    description:
      "Volume I introduces the institutional problems that Trading Truth Layer exists to solve and establishes the foundations of Institutional Trading Trust Infrastructure.",

    status: "AVAILABLE" as const,

    downloadUrl:
    `${BACKEND_URL}/api/reports/guidebooks/volume-1/download`,

    readUrl:
    `${BACKEND_URL}/api/reports/guidebooks/volume-1/view`,
  },

  {
    volume: "VOLUME II",

    title:
      "Verification Infrastructure",

    description:
      "Institutional verification standards, evidence systems and canonical trust infrastructure.",

    status: "COMING SOON" as const,
  },

  {
    volume: "VOLUME III",

    title:
      "Institutional Due Diligence Infrastructure",

    description:
      "Allocator readiness, due diligence systems and institutional investigation architecture.",

    status: "COMING SOON" as const,
  },

  {
    volume: "VOLUME IV",

    title:
      "Institutional Capital Allocation Infrastructure",

    description:
      "The evolution of capital allocation through evidence-based trust infrastructure.",

    status: "COMING SOON" as const,
  },
];