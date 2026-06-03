"use client";

import { useEffect } from "react";

declare global {
  interface Window {
    Paddle?: any;
  }
}

export default function PaddleLoader() {
  useEffect(() => {
    const clientToken =
      process.env.NEXT_PUBLIC_PADDLE_CLIENT_TOKEN;

    if (!clientToken) {
      console.error(
        "Paddle client token missing."
      );
      return;
    }

    const existing = document.querySelector(
      'script[src="https://cdn.paddle.com/paddle/v2/paddle.js"]'
    );

    if (existing) {
      initializePaddle(clientToken);
      return;
    }

    const script = document.createElement("script");

    script.src =
      "https://cdn.paddle.com/paddle/v2/paddle.js";

    script.async = true;

    script.onload = () => {
      initializePaddle(clientToken);
    };

    document.body.appendChild(script);

    return () => {
      document.body.removeChild(script);
    };
  }, []);

  return null;
}

function initializePaddle(
  clientToken: string
) {
  if (!window.Paddle) {
    console.error(
      "Paddle SDK failed to load."
    );
    return;
  }

  console.log(
    "CLIENT TOKEN PREFIX:",
    clientToken.substring(0, 20)
  );

  try {
    window.Paddle.Initialize({
      token: clientToken,
    });

    console.log(
      "Paddle initialized successfully."
    );

    const params = new URLSearchParams(
      window.location.search
    );

    const transactionId =
      params.get("_ptxn");

    if (transactionId) {
      console.log(
          "Opening Paddle checkout for transaction:",
          transactionId
      );

      window.Paddle.Checkout.open({
          transactionId,

          settings: {
          displayMode: "overlay"
          }
      });
      }
  } catch (err) {
    console.error(
      "Paddle initialization failed:",
      err
    );
  }
}