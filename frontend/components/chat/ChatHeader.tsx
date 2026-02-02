import { X } from "lucide-react";

interface ChatHeaderProps {
  onClose: () => void;
}

export function ChatHeader({ onClose }: ChatHeaderProps) {
  return (
    <div className="flex items-center justify-between p-4 border-b bg-blue-600 text-white rounded-t-lg">
      <div>
        <h3 className="font-semibold">AI Financial Assistant</h3>
        <p className="text-xs text-blue-100">Ask me anything about your finances</p>
      </div>
      <button
        onClick={onClose}
        className="text-white hover:bg-blue-700 rounded p-1 transition-colors"
      >
        <X className="h-5 w-5" />
      </button>
    </div>
  );
}
