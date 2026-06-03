import { Outlet, Link } from "react-router-dom";

export default function PublicLayout() {
  return (
    <div className="min-h-screen bg-[#020817] text-white">
      {/* TOP NAV */}
      <header className="border-b border-slate-800">
        <div className="max-w-7xl mx-auto px-8 h-20 flex items-center justify-between">
          <Link
            to="/welcome"
            className="text-2xl font-black"
          >
            Trading Truth Layer
          </Link>

          <nav className="flex items-center gap-6 text-sm">
            <Link
              to="/pricing"
              className="text-slate-300 hover:text-white"
            >
              Pricing
            </Link>

            <Link
              to="/download"
              className="text-slate-300 hover:text-white"
            >
              Download
            </Link>

            <Link
              to="/contact"
              className="text-slate-300 hover:text-white"
            >
              Contact
            </Link>
          </nav>
        </div>
      </header>

      {/* PAGE */}
      <Outlet />
    </div>
  );
}