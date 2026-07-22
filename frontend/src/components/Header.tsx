import { FlaskConical, Radio } from "lucide-react";
import type { WorkspaceTab } from "../App";

interface HeaderProps {
  online: boolean;
  activeTab: WorkspaceTab;
  onNavigate: (tab: WorkspaceTab) => void;
  onPaperVaultClick: () => void;
}

export function Header({
  online,
  activeTab,
  onNavigate,
  onPaperVaultClick,
}: HeaderProps) {
  return (
    <header className="site-header">
      <button
        type="button"
        className="brand brand-button"
        onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
        aria-label="Back to the top"
      >
        <span className="brand-mark">
          <FlaskConical size={25} strokeWidth={2.6} />
        </span>

        <span>
          <strong>ResearchIQ</strong>
          <small>Experimental paper laboratory</small>
        </span>
      </button>

      <nav className="header-nav" aria-label="Primary navigation">
        <button
          type="button"
          onClick={onPaperVaultClick}

        >
          Paper Vault
        </button>

        <button
          type="button"
          className={activeTab === "search" ? "active" : ""}
          onClick={() => onNavigate("search")}
        >
          Research Console
        </button>

        <button
          type="button"
          className={activeTab === "comparison" ? "active" : ""}
          onClick={() => onNavigate("comparison")}
        >
          Comparison Reactor
        </button>
      </nav>

      <div className="header-actions">
        <span className={`status-chip ${online ? "online" : "offline"}`}>
          <Radio size={14} />
          {online ? "System online" : "System offline"}
        </span>
      </div>
    </header>
  );
}
