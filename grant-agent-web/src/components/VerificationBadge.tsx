import React from "react";
import { VerificationStatus } from "../types";

export function VerificationBadge({ status }: { status: VerificationStatus | string }) {
  if (status === "VERIFIED") {
    return (
      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded text-xs font-semibold bg-emerald-100 text-emerald-800">
        <svg className="w-3 h-3 fill-current" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
        </svg>
        VERIFIED
      </span>
    );
  }
  if (status === "UNVERIFIED") {
    return (
      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded text-xs font-semibold bg-slate-100 text-slate-700">
        UNVERIFIED
      </span>
    );
  }
  return (
    <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded text-xs font-semibold bg-rose-100 text-rose-800">
      DO NOT USE
    </span>
  );
}
