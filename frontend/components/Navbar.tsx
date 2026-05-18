"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";

export default function Navbar() {
  const router = useRouter();

  function handleLogout() {
    localStorage.removeItem("access_token");
    router.push("/login");
  }

  return (
    <nav className="bg-white border-b shadow-sm px-8 py-4 flex items-center justify-between">
      <div className="font-bold text-xl">
        Stock Tracker
      </div>

      <div className="flex items-center gap-4">
        <Link href="/dashboard" className="hover:underline">
          Dashboard
        </Link>

        <Link href="/holdings" className="hover:underline">
          Holdings
        </Link>

        <button
          onClick={handleLogout}
          className="bg-black text-white rounded-lg px-4 py-2 text-sm"
        >
          Logout
        </button>
      </div>
    </nav>
  );
}
