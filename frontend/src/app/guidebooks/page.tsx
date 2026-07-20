"use client";

import { GUIDEBOOKS } from "@/lib/guidebooks";

export default function GuidebooksPage() {
  return (
    <main
      style={{
        maxWidth: 1200,
        margin: "0 auto",
        padding: "48px 24px",
      }}
    >
      {/* HERO */}

      <div
        style={{
          marginBottom: 48,
        }}
      >
        <div
          style={{
            fontSize: 14,
            letterSpacing: 2,
            color: "#64748b",
            fontWeight: 700,
            textTransform: "uppercase",
            marginBottom: 12,
          }}
        >
          Trading Truth Layer
        </div>

        <h1
          style={{
            fontSize: 52,
            margin: 0,
            color: "#0f172a",
          }}
        >
          Institutional Guidebook Series
        </h1>

        <p
          style={{
            marginTop: 20,
            lineHeight: 1.9,
            fontSize: 18,
            maxWidth: 900,
            color: "#475569",
          }}
        >
          The Trading Truth Layer Guidebook Series
          introduces the institutional theories,
          infrastructure and verification standards
          required to establish Institutional Trading
          Trust Infrastructure across global capital
          markets.
        </p>
      </div>

      {/* GUIDEBOOKS */}

      <div
        style={{
          display: "grid",
          gap: 24,
        }}
      >
        {GUIDEBOOKS.map((guidebook) => (
          <div
            key={guidebook.volume}
            style={{
              background: "#ffffff",
              border: "1px solid #e5e7eb",
              borderRadius: 16,
              padding: 32,
            }}
          >
            <div
              style={{
                fontSize: 13,
                fontWeight: 700,
                letterSpacing: 1.5,
                color: "#64748b",
                marginBottom: 12,
              }}
            >
              {guidebook.volume}
            </div>

            <h2
              style={{
                marginTop: 0,
                marginBottom: 18,
                color: "#0f172a",
              }}
            >
              {guidebook.title}
            </h2>

            <p
              style={{
                lineHeight: 1.9,
                color: "#475569",
                marginBottom: 28,
                maxWidth: 850,
              }}
            >
              {guidebook.description}
            </p>

            <div
              style={{
                display: "flex",
                gap: 12,
                flexWrap: "wrap",
              }}
            >
              {guidebook.status === "AVAILABLE" ? (
                <>
                  <a
                    href={guidebook.downloadUrl}
                    target="_blank"
                    rel="noreferrer"
                    style={{
                      textDecoration: "none",
                      padding: "12px 20px",
                      borderRadius: 10,
                      background: "#0f172a",
                      color: "#ffffff",
                      fontWeight: 600,
                    }}
                  >
                    {`Download ${guidebook.volume}`}
                  </a>

                  <a
                    href={guidebook.readUrl}
                    target="_blank"
                    rel="noreferrer"
                    style={{
                        textDecoration: "none",
                        padding: "12px 20px",
                        borderRadius: 10,
                        border: "1px solid #cbd5e1",
                        color: "#0f172a",
                        fontWeight: 600,
                    }}
                >
                    Learn More
                </a>
                </>
              ) : (
                <div
                  style={{
                    padding: "12px 20px",
                    borderRadius: 10,
                    background: "#f1f5f9",
                    color: "#475569",
                    fontWeight: 600,
                  }}
                >
                  Coming Soon
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </main>
  );
}