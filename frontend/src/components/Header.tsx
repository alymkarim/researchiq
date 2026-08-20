import { RadioTower } from "lucide-react";

import type { WorkspaceTab } from "../App";
import { ThemeToggle } from "./ThemeToggle";

interface HeaderProps {
  online: boolean;
  activeTab: WorkspaceTab;
  onNavigate: (tab: WorkspaceTab) => void;
  onPaperVaultClick: () => void;
}

const NAV_ITEMS: { label: string; tab: WorkspaceTab }[] = [
  { label: "Overview", tab: "overview" },
  { label: "Search", tab: "search" },
  { label: "Analysis", tab: "analysis" },
  { label: "Compare", tab: "comparison" },
];

export function Header({
  online,
  activeTab,
  onNavigate,
  onPaperVaultClick,
}: HeaderProps) {
  function goToTop() {
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  return (
    <header className="site-header">
      <button
        type="button"
        className="brand brand-button"
        onClick={goToTop}
        aria-label="Back to the top"
      >
        <span className="brand-name">ResearchIQ</span>
      </button>

      <nav className="header-nav" aria-label="Primary navigation">
        {NAV_ITEMS.map(({ label, tab }) => (
          <button
            key={tab}
            type="button"
            className={activeTab === tab ? "active" : ""}
            onClick={() => onNavigate(tab)}
          >
            {label}
          </button>
        ))}

        <button type="button" onClick={onPaperVaultClick}>
          Paper Vault
        </button>
      </nav>

      <div className="header-actions">
        <ThemeToggle />

        <span
          className={`status-chip ${online ? "online" : "offline"}`}
        >
          <RadioTower size={14} />
          {online ? "Online" : "Offline"}
        </span>
      </div>
    </header>
  );
}
