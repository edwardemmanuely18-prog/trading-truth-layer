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
      "Institutional Verification Infrastructure",

    description:
      "Volume II introduces the institutional verification standards, verification infrastructure, evidence systems and institutional workflows required to independently establish trust in trading performance.",

    status: "AVAILABLE" as const,

    downloadUrl:
      `${BACKEND_URL}/api/reports/guidebooks/volume-2/download`,

    readUrl:
      `${BACKEND_URL}/api/reports/guidebooks/volume-2/view`,
  },

  {
      volume: "VOLUME III",

      title:
      "Trading Verification Infrastructure",

      description:
      "Institutional verification standards, institutional trust artifacts and allocator-ready verification infrastructure.",

      status: "AVAILABLE" as const,

      downloadUrl:
      `${BACKEND_URL}/api/reports/guidebooks/volume-3/download`,

      readUrl:
      `${BACKEND_URL}/api/reports/guidebooks/volume-3/view`,
  },

  {
      volume: "VOLUME IV",

      title:
        "Institutional Capital Allocation Infrastructure",

      description:
        "Institutional trust infrastructure for evidence-based capital allocation across the entire Trading Truth Layer workspace and public trust ecosystem.",

      status: "AVAILABLE" as const,

      downloadUrl:
        `${BACKEND_URL}/api/reports/guidebooks/volume-4/download`,

      readUrl:
        `${BACKEND_URL}/api/reports/guidebooks/volume-4/view`,
  },

];