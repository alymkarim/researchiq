import {
  CalendarDays,
  Check,
  FileText,
  FolderOpen,
  LoaderCircle,
  Microscope,
  Trash2,
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

function formatDate(value?: string | null) {
  if (!value) return "Recently uploaded";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return new Intl.DateTimeFormat("en", {
    day: "numeric",
    month: "short",
    year: "numeric",
  }).format(date);
}

function SkeletonCard() {
  return (
    <div className="paper-card skeleton">
      <div className="paper-card-skeleton-icon" />
      <div className="paper-card-skeleton-body">
        <div className="paper-card-skeleton-title" />
        <div className="paper-card-skeleton-text" />
        <div className="paper-card-skeleton-text short" />
      </div>
    </div>
  );
}

function getStatusBadge(document: DocumentItem) {
  if (document.analysis) {
    return document.analysis.analysis_mode === "llm"
      ? { label: "LLM analysed", className: "badge-analysed-llm" }
      : { label: "Analysed", className: "badge-analysed" };
  }
  return null;
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
    <section className="paper-vault" id="vault">
      <div className="panel-heading">
        <div>
          <span className="panel-kicker">Secure archive</span>
          <h2>Paper Vault</h2>
        </div>
        <div className="vault-toolbar">
          <span className="vault-count">{documents.length} papers</span>
          {selectedIds.length > 0 && (
            <span className="vault-selected">{selectedIds.length} selected</span>
          )}
        </div>
      </div>

      {loading ? (
        <div className="paper-grid">
          <SkeletonCard />
          <SkeletonCard />
          <SkeletonCard />
        </div>
      ) : documents.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">
            <FolderOpen size={40} />
          </div>
          <h3>The vault is empty</h3>
          <p>Upload a PDF to begin your research analysis.</p>
        </div>
      ) : (
        <div className="paper-grid">
          {documents.map((document) => {
            const selected = selectedIds.includes(document.id);
            const badge = getStatusBadge(document);
            const isAnalysing = analysingId === document.id;

            return (
              <article
                className={`paper-card ${selected ? "selected" : ""}`}
                key={document.id}
              >
                <div className="paper-card-header">
                  <button
                    className="paper-toggle"
                    onClick={() => onToggle(document.id)}
                    aria-pressed={selected}
                    aria-label={`Select ${document.title || document.filename}`}
                  >
                    {selected && <Check size={12} />}
                  </button>

                  <div className="paper-card-icon">
                    <FileText size={20} />
                  </div>

                  {badge && (
                    <span className={`paper-badge ${badge.className}`}>
                      {badge.label}
                    </span>
                  )}
                </div>

                <div className="paper-card-body">
                  <h3 className="paper-card-title">
                    {document.title || document.filename}
                  </h3>

                  <div className="paper-card-meta">
                    {document.authors && (
                      <span className="paper-card-authors">
                        {document.authors}
                      </span>
                    )}
                    <span className="paper-card-date">
                      <CalendarDays size={13} />
                      {formatDate(document.created_at)}
                    </span>
                  </div>
                </div>

                <div className="paper-card-actions">
                  <button
                    className="btn-paper btn-analyse"
                    onClick={() => onAnalyse(document.id)}
                    disabled={isAnalysing}
                  >
                    {isAnalysing ? (
                      <LoaderCircle className="spin" size={15} />
                    ) : (
                      <Microscope size={15} />
                    )}
                    {isAnalysing ? "Analysing" : "Analyse"}
                  </button>
                  <button
                    className="btn-paper btn-delete"
                    onClick={() => onDelete(document.id)}
                  >
                    <Trash2 size={15} />
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
