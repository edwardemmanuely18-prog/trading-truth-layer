import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import "./index.css";

import App from "./App.jsx";

import { RuntimeProvider }
from "./providers/RuntimeProvider";

import { bootstrapRuntime }
from "./services/runtime/runtimeBootstrap";

/* =========================================
   RUNTIME BOOTSTRAP
========================================= */

bootstrapRuntime();

/* =========================================
   ROOT RENDER
========================================= */

createRoot(
  document.getElementById("root")
).render(
  <StrictMode>
    <RuntimeProvider>
      <App />
    </RuntimeProvider>
  </StrictMode>
);