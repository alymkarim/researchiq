import { AlertTriangle, CheckCircle2, X } from "lucide-react";

interface ToastProps {
  message: string;
  type: "success" | "error";
  onClose: () => void;
}

export function Toast({ message, type, onClose }: ToastProps) {
  return (
    <div className={`toast ${type}`} role="status">
      {type === "success" ? (
        <CheckCircle2 size={20} />
      ) : (
        <AlertTriangle size={20} />
      )}
      <span>{message}</span>
      <button onClick={onClose} aria-label="Dismiss notification">
        <X size={17} />
      </button>
    </div>
  );
}
