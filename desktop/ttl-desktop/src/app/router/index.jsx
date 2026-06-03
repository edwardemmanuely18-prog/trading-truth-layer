import {
  BrowserRouter,
  Routes,
  Route,
} from "react-router-dom";

import MainLayout from "../../layouts/MainLayout";
import PublicLayout from "../../layouts/PublicLayout";

import { appRoutes } from "./routes";
import { publicRoutes } from "../../routes/publicRoutes";

export default function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>

        {/* PUBLIC WEBSITE */}
        <Route element={<PublicLayout />}>
          {publicRoutes.map((route) => (
            <Route
              key={route.path}
              path={route.path}
              element={route.element}
            />
          ))}
        </Route>

        {/* DESKTOP PLATFORM */}
        <Route path="/" element={<MainLayout />}>
          {appRoutes.map((route) => (
            <Route
              key={route.path}
              path={route.path}
              element={route.element}
            />
          ))}
        </Route>

      </Routes>
    </BrowserRouter>
  );
}