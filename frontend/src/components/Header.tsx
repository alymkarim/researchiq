import {
  Atom,
  FlaskConical,
  Github,
  RadioTower,
} from "lucide-react";

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
  function goToTop() {
    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  }

  return (
    <header className="site-header">
      <button
        type="button"
        className="brand brand-button"
        onClick={goToTop}
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

      <nav
        className="header-nav"
        aria-label="Primary navigation"
      >
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
          className={
            activeTab === "comparison" ? "active" : ""
          }
          onClick={() => onNavigate("comparison")}
        >
          Comparison Reactor
        </button>
      </nav>

      <div className="header-actions">
        <span
          className={`status-chip ${
            online ? "online" : "offline"
          }`}
        >
          <RadioTower size={14} />

          {online ? "System online" : "System offline"}
        </span>

        <a
          className="icon-button"
          href="https://github.com/alymkarim/researchiq"
          target="_blank"
          rel="noreferrer"
          aria-label="Open ResearchIQ on GitHub"
        >
          <Github size={19} />
        </a>
      </div>

      <Atom
        className="header-atom"
        aria-hidden="true"
      />
    </header>
  );
}