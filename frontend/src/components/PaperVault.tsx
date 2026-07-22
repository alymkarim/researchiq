import {
  CalendarDays,
  FileText,
  LoaderCircle,
  Microscope,
  Trash2,
  UserRound,
} from "lucide-react";
import type { DocumentItem } from "../types";

interface PaperVaultProps {
  documents: DocumentItem[];
  loading: boolean;
  selectedIds: number[];
  analysingId: number | null;
  onToggle: (id: number) => void;
  onAnalyse: (id: number) => Promise<void>;
  onDelete: (id: number) => Promise<void>;
}

function formatDate(value?: string) {
  if (!value) return "Recently uploaded";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;

  return new Intl.DateTimeFormat("en", {
    day: "numeric",
    month: "short",
    year: "numeric",
  }).format(date);
}

export function PaperVault({
  documents,
  loading,
  selectedIds,
  analysingId,
  onToggle,
  onAnalyse,
  onDelete,
}: PaperVaultProps) {
  return (
    <section className="lab-panel paper-vault" id="vault">
      <div className="panel-heading">
        <div>
          <span className="section-kicker">Secure archive</span>
          <h2>Paper Vault</h2>
        </div>
        <span className="panel-number">02</span>
      </div>

      <div className="vault-toolbar">
        <span>{documents.length} specimens catalogued</span>
        <span>{selectedIds.length} selected</span>
      </div>

      {loading ? (
        <div className="empty-state">
          <LoaderCircle className="spin" size={34} />
          <strong>Opening vault...</strong>
        </div>
      ) : documents.length === 0 ? (
        <div className="empty-state">
          <FileText size={38} />
          <strong>The vault is tragically empty.</strong>
          <span>Add a PDF and let the scientific meddling begin.</span>
        </div>
      ) : (
        <div className="paper-list">
          {documents.map((document) => {
            const selected = selectedIds.includes(document.id);
            return (
              <article
                className={`paper-card ${selected ? "selected" : ""}`}
                key={document.id}
              >
                <button
                  className="paper-select"
                  onClick={() => onToggle(document.id)}
                  aria-pressed={selected}
                  aria-label={`${selected ? "Deselect" : "Select"} ${
                    document.title || document.filename
                  }`}
                >
                  <span>{selected ? "✓" : ""}</span>
                </button>

                <div className="paper-icon">
                  <FileText size={25} />
                </div>

                <div className="paper-content">
                  <span className="paper-id">
                    SPECIMEN #{String(document.id).padStart(3, "0")}
                  </span>

                  <h3>{document.title || document.filename}</h3>

                  <p>
                    {document.abstract ||
                      "Abstract unavailable. The machine remains dramatically mysterious."}
                  </p>

                  <div className="paper-meta">
                    <span>
                      <UserRound size={14} />
                      {document.authors || "Unknown researchers"}
                    </span>
                    <span>
                      <CalendarDays size={14} />
                      {formatDate(document.created_at)}
                    </span>
                  </div>
                </div>

                <div className="paper-actions">
                  <button
                    className="small-action analyse"
                    onClick={() => onAnalyse(document.id)}
                    disabled={analysingId === document.id}
                  >
                    {analysingId === document.id ? (
                      <LoaderCircle className="spin" size={16} />
                    ) : (
                      <Microscope size={16} />
                    )}
                    Analyse
                  </button>

                  <button
                    className="small-action danger"
                    onClick={() => onDelete(document.id)}
                  >
                    <Trash2 size={16} />
                    Incinerate
                  </button>
                </div>
              </article>
            );
          })}
        </div>
      )}
    </section>
  );
}
