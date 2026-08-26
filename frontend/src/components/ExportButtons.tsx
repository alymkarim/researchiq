import { Download, FileText, FileSpreadsheet } from "lucide-react";

interface ExportButtonsProps {
  documentId: number;
  documentTitle: string;
}

export function ExportButtons({ documentId, documentTitle }: ExportButtonsProps) {
  const baseUrl = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

  function getExportUrl(format: "pdf" | "docx"): string {
    const stored = localStorage.getItem("researchiq-auth");
    let token = "";
    if (stored) {
      try {
        const parsed = JSON.parse(stored) as { token?: string };
        token = parsed.token || "";
      } catch {
        /* ignore */
      }
    }
    return `${baseUrl}/api/export/analysis/${documentId}/${format}${token ? `?token=${token}` : ""}`;
  }

  return (
    <div className="export-buttons">
      <span className="export-label">
        <Download size={14} />
        Export Analysis
      </span>
      <a
        href={getExportUrl("pdf")}
        className="export-btn"
        download={`${documentTitle || "analysis"}.pdf`}
        target="_blank"
        rel="noopener noreferrer"
      >
        <FileText size={14} />
        PDF
      </a>
      <a
        href={getExportUrl("docx")}
        className="export-btn"
        download={`${documentTitle || "analysis"}.docx`}
        target="_blank"
        rel="noopener noreferrer"
      >
        <FileSpreadsheet size={14} />
        DOCX
      </a>
    </div>
  );
}
