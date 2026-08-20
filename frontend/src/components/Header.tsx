import { LogOut, RadioTower } from "lucide-react";

import type { WorkspaceTab } from "../App";
import { useAuth } from "../context/AuthContext";
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
  const { user, logout } = useAuth();

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

        {user && (
          <>
            <span className="header-username">
              {user.username}
            </span>
            <button
              type="button"
              className="header-logout"
              onClick={logout}
              title="Sign out"
            >
              <LogOut size={16} />
            </button>
          </>
        )}
      </div>
    </header>
  );
}
