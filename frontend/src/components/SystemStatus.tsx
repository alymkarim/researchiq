import { useEffect, useState } from "react";
import { CircleAlert, LoaderCircle, Radio } from "lucide-react";
import type { HealthStatus } from "../types";

const API_URL =
  import.meta.env.VITE_API_URL || "http://localhost:8000";

export function SystemStatus() {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;

    async function checkHealth() {
      try {
        const response = await fetch(`${API_URL}/api/health`);

        if (!response.ok) {
          throw new Error("Health check failed");
        }

        const data: HealthStatus = await response.json();

        if (active) {
          setHealth(data);
        }
      } catch {
        if (active) {
          setHealth(null);
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    void checkHealth();

    return () => {
      active = false;
    };
  }, []);

  if (loading) {
    return (
      <div className="system-status checking">
        <LoaderCircle className="spin" size={15} />
        Checking research engine
      </div>
    );
  }

  if (!health || health.status !== "healthy") {
    return (
      <div className="system-status offline">
        <CircleAlert size={15} />
        Research engine unavailable
      </div>
    );
  }

  return (
    <div className="system-status online">
      <Radio size={15} />
      Research engine online
    </div>
  );
}