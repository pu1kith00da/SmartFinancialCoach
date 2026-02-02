"use client";

import { cn } from "@/lib/utils";

interface PasswordStrengthProps {
  password: string;
}

export function PasswordStrength({ password }: PasswordStrengthProps) {
  const calculateStrength = (pwd: string): { score: number; label: string; color: string } => {
    let score = 0;

    if (pwd.length >= 8) score++;
    if (pwd.length >= 12) score++;
    if (/[a-z]/.test(pwd) && /[A-Z]/.test(pwd)) score++;
    if (/\d/.test(pwd)) score++;
    if (/[!@#$%^&*(),.?":{}|<>]/.test(pwd)) score++;

    const strengths = [
      { score: 0, label: "Very Weak", color: "bg-red-500" },
      { score: 1, label: "Weak", color: "bg-orange-500" },
      { score: 2, label: "Fair", color: "bg-yellow-500" },
      { score: 3, label: "Good", color: "bg-lime-500" },
      { score: 4, label: "Strong", color: "bg-green-500" },
      { score: 5, label: "Very Strong", color: "bg-emerald-600" },
    ];

    return strengths[score];
  };

  if (!password) return null;

  const strength = calculateStrength(password);
  const percentage = (strength.score / 5) * 100;

  return (
    <div className="mt-2 space-y-2">
      <div className="h-2 w-full overflow-hidden rounded-full bg-gray-200">
        <div
          className={cn("h-full transition-all duration-300", strength.color)}
          style={{ width: `${percentage}%` }}
        />
      </div>
      <div className="flex items-center justify-between text-xs">
        <span className="text-muted-foreground">Password strength:</span>
        <span className={cn("font-medium", strength.color.replace("bg-", "text-"))}>
          {strength.label}
        </span>
      </div>
      <ul className="space-y-1 text-xs text-muted-foreground">
        <li className={password.length >= 12 ? "text-green-600" : ""}>
          {password.length >= 12 ? "✓" : "○"} At least 12 characters
        </li>
        <li className={/[A-Z]/.test(password) ? "text-green-600" : ""}>
          {/[A-Z]/.test(password) ? "✓" : "○"} One uppercase letter
        </li>
        <li className={/[a-z]/.test(password) ? "text-green-600" : ""}>
          {/[a-z]/.test(password) ? "✓" : "○"} One lowercase letter
        </li>
        <li className={/\d/.test(password) ? "text-green-600" : ""}>
          {/\d/.test(password) ? "✓" : "○"} One number
        </li>
        <li className={/[!@#$%^&*(),.?":{}|<>]/.test(password) ? "text-green-600" : ""}>
          {/[!@#$%^&*(),.?":{}|<>]/.test(password) ? "✓" : "○"} One special character
        </li>
      </ul>
    </div>
  );
}
