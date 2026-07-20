type GuidebookVolumeCardProps = {
  volume: string;
  title: string;
  description: string;
  status: "AVAILABLE" | "COMING SOON";
  downloadUrl?: string;
  readUrl?: string;
};

export default function GuidebookVolumeCard({
  volume,
  title,
  description,
  status,
  downloadUrl,
  readUrl,
}: GuidebookVolumeCardProps) {
  return (
    <section
      style={{
        background: "#ffffff",
        border: "1px solid #e5e7eb",
        borderRadius: 16,
        padding: 32,
      }}
    >
      {/* Volume */}

      <div
        style={{
          fontSize: 14,
          fontWeight: 700,
          letterSpacing: "0.15em",
          textTransform: "uppercase",
          color: "#64748b",
          marginBottom: 8,
        }}
      >
        {volume}
      </div>

      {/* Title */}

      <h2
        style={{
          margin: 0,
          fontSize: 30,
          fontWeight: 800,
          color: "#0f172a",
        }}
      >
        {title}
      </h2>

      {/* Status */}

      <div
        style={{
          marginTop: 18,
          display: "inline-block",
          padding: "6px 14px",
          borderRadius: 9999,
          border: "1px solid #cbd5e1",
          fontSize: 13,
          fontWeight: 700,
          color: "#334155",
        }}
      >
        {status}
      </div>

      {/* Description */}

      <p
        style={{
          marginTop: 24,
          marginBottom: 0,
          fontSize: 16,
          lineHeight: 1.9,
          color: "#475569",
          maxWidth: 900,
        }}
      >
        {description}
      </p>

      {/* Buttons */}

      {status === "AVAILABLE" && (
        <div
          style={{
            display: "flex",
            gap: 16,
            marginTop: 32,
            flexWrap: "wrap",
          }}
        >
          {readUrl && (
            <a
              href={readUrl}
              style={{
                textDecoration: "none",
                padding: "12px 24px",
                borderRadius: 12,
                border: "1px solid #0f172a",
                color: "#0f172a",
                fontWeight: 700,
              }}
            >
              Read Online
            </a>
          )}

          {downloadUrl && (
            <a
              href={downloadUrl}
              target="_blank"
              rel="noreferrer"
              style={{
                textDecoration: "none",
                padding: "12px 24px",
                borderRadius: 12,
                background: "#0f172a",
                color: "#ffffff",
                fontWeight: 700,
              }}
            >
              Download PDF
            </a>
          )}
        </div>
      )}
    </section>
  );
}