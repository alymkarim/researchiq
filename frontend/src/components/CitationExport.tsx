import { useState } from "react";
import { Check, Copy } from "lucide-react";
import { getCitation } from "../api";

interface CitationExportProps {
  documentId: number;
}

type CitationFormat = "bibtex" | "apa" | "mla";

const FORMAT_LABELS: Record<CitationFormat, string> = {
  bibtex: "BibTeX",
  apa: "APA",
  mla: "MLA",
};

export function CitationExport({ documentId }: CitationExportProps) {
  const [format, setFormat] = useState<CitationFormat>("bibtex");
  const [citation, setCitation] = useState<string>("");
  const [copied, setCopied] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchCitation = async (selectedFormat: CitationFormat) => {
    setFormat(selectedFormat);
    setLoading(true);
    setError(null);
    setCopied(false);

    try {
      const result = await getCitation(documentId, selectedFormat);
      setCitation(result.citation);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch citation");
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = async () => {
    if (!citation) return;

    try {
      await navigator.clipboard.writeText(citation);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      setError("Failed to copy to clipboard");
    }
  };

  return (
    <div className="citation-export">
      <div className="citation-header">
        <h3>Export Citation</h3>
        <div className="citation-formats">
          {(Object.keys(FORMAT_LABELS) as CitationFormat[]).map((fmt) => (
            <button
              key={fmt}
              className={`citation-format-btn ${format === fmt ? "active" : ""}`}
              onClick={() => fetchCitation(fmt)}
            >
              {FORMAT_LABELS[fmt]}
            </button>
          ))}
        </div>
      </div>

      {loading && <div className="citation-loading">Loading citation...</div>}

      {error && <div className="citation-error">{error}</div>}

      {citation && !loading && (
        <div className="citation-content">
          <pre className="citation-text">{citation}</pre>
          <button
            className={`citation-copy-btn ${copied ? "copied" : ""}`}
            onClick={copyToClipboard}
          >
            {copied ? (
              <>
                <Check size={14} /> Copied
              </>
            ) : (
              <>
                <Copy size={14} /> Copy
              </>
            )}
          </button>
        </div>
      )}
    </div>
  );
}
