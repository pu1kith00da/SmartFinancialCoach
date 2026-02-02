interface ChatSuggestionsProps {
  onSelect: (question: string) => void;
}

const SUGGESTED_QUESTIONS = [
  "How much did I spend this month?",
  "What are my top spending categories?",
  "Show my recent transactions",
  "How am I doing on my savings goals?",
  "Where can I save money?",
  "Compare my spending to last month",
];

export function ChatSuggestions({ onSelect }: ChatSuggestionsProps) {
  return (
    <div className="p-4 bg-gray-50 border-b">
      <p className="text-xs text-gray-600 mb-2">Try asking:</p>
      <div className="flex flex-wrap gap-2">
        {SUGGESTED_QUESTIONS.map((question, index) => (
          <button
            key={index}
            onClick={() => onSelect(question)}
            className="px-3 py-1 text-xs bg-white border border-gray-300 rounded-full hover:bg-blue-50 hover:border-blue-300 transition-colors"
          >
            {question}
          </button>
        ))}
      </div>
    </div>
  );
}
