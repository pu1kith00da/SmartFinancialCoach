export default function Home() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-gradient-to-br from-blue-50 via-white to-purple-50 p-8">
      <div className="mx-auto max-w-4xl text-center">
        <h1 className="mb-4 text-6xl font-bold tracking-tight text-gray-900">
          Smart Financial Coach
        </h1>
        <p className="mb-8 text-xl text-gray-600">
          AI-powered financial insights to transform your money habits
        </p>
        <div className="flex gap-4 justify-center">
          <a
            href="/login"
            className="rounded-lg bg-blue-600 px-8 py-3 text-lg font-semibold text-white transition hover:bg-blue-700"
          >
            Get Started
          </a>
          <a
            href="/register"
            className="rounded-lg border-2 border-blue-600 px-8 py-3 text-lg font-semibold text-blue-600 transition hover:bg-blue-50"
          >
            Sign Up
          </a>
        </div>
        
        <div className="mt-16 grid gap-8 md:grid-cols-3">
          <div className="rounded-lg bg-white p-6 shadow-md">
            <div className="mb-4 text-4xl">📊</div>
            <h3 className="mb-2 text-xl font-semibold">Smart Analytics</h3>
            <p className="text-gray-600">
              AI-powered insights into your spending patterns
            </p>
          </div>
          
          <div className="rounded-lg bg-white p-6 shadow-md">
            <div className="mb-4 text-4xl">🎯</div>
            <h3 className="mb-2 text-xl font-semibold">Goal Tracking</h3>
            <p className="text-gray-600">
              Set and achieve your financial goals
            </p>
          </div>
          
          <div className="rounded-lg bg-white p-6 shadow-md">
            <div className="mb-4 text-4xl">🔒</div>
            <h3 className="mb-2 text-xl font-semibold">Bank-Level Security</h3>
            <p className="text-gray-600">
              Your data is encrypted and protected
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
