import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Authentication - Smart Financial Coach",
  description: "Sign in or create an account",
};

export default function AuthLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <div className="flex min-h-screen">
      {/* Left side - Branding */}
      <div className="hidden w-1/2 bg-gradient-to-br from-blue-600 via-blue-700 to-purple-700 lg:flex lg:flex-col lg:justify-center lg:p-12">
        <div className="mx-auto max-w-md text-white">
          <h1 className="mb-6 text-4xl font-bold">Smart Financial Coach</h1>
          <p className="mb-8 text-lg text-blue-100">
            Transform your financial life with AI-powered insights and personalized coaching.
          </p>
          <div className="space-y-4">
            <div className="flex items-start gap-3">
              <div className="rounded-full bg-white/20 p-2">
                <svg
                  className="h-5 w-5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
              </div>
              <div>
                <h3 className="font-semibold">Automated Insights</h3>
                <p className="text-sm text-blue-100">AI analyzes your spending and provides actionable tips</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <div className="rounded-full bg-white/20 p-2">
                <svg
                  className="h-5 w-5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
                  />
                </svg>
              </div>
              <div>
                <h3 className="font-semibold">Bank-Level Security</h3>
                <p className="text-sm text-blue-100">Your data is encrypted and protected</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <div className="rounded-full bg-white/20 p-2">
                <svg
                  className="h-5 w-5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M13 10V3L4 14h7v7l9-11h-7z"
                  />
                </svg>
              </div>
              <div>
                <h3 className="font-semibold">Real-time Sync</h3>
                <p className="text-sm text-blue-100">Automatically sync transactions from your bank</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Right side - Form */}
      <div className="flex w-full flex-col justify-center p-8 lg:w-1/2">
        <div className="mx-auto w-full max-w-md">{children}</div>
      </div>
    </div>
  );
}
