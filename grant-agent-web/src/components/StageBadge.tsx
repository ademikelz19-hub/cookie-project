import React from "react";
import { GrantStageClassification } from "../types";

export function StageBadge({ stage }: { stage: GrantStageClassification | string }) {
  if (stage === "GREEN — IDEA STAGE" || stage.includes("IDEA")) {
    return (
      <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
        <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
        IDEA STAGE · No MVP Required
      </span>
    );
  }
  if (stage === "YELLOW — VALIDATION STAGE" || stage.includes("VALIDATION")) {
    return (
      <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-amber-50 text-amber-700 border border-amber-200">
        <span className="w-2 h-2 rounded-full bg-amber-500" />
        VALIDATION STAGE · Prototype / PoC
      </span>
    );
  }
  if (stage === "ORANGE — MVP REQUIRED" || stage.includes("MVP")) {
    return (
      <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-orange-50 text-orange-700 border border-orange-200">
        <span className="w-2 h-2 rounded-full bg-orange-500" />
        MVP REQUIRED · Working Demo Needed
      </span>
    );
  }
  return (
    <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-rose-50 text-rose-700 border border-rose-200">
      <span className="w-2 h-2 rounded-full bg-rose-500" />
      TRACTION REQUIRED · Revenue / Users
    </span>
  );
}
