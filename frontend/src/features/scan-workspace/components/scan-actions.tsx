"use client";

import { RotateCcw } from "lucide-react";

import { Button } from "@/components/ui/button";

interface ScanActionsProps {
  onScanCode: () => void;
  onScanFile: () => void;
  onNewScan?: () => void;
  disableCodeScan: boolean;
  disableFileScan: boolean;
  isScanning: boolean;
  showNewScan?: boolean;
}

export function ScanActions({
  onScanCode,
  onScanFile,
  onNewScan,
  disableCodeScan,
  disableFileScan,
  isScanning,
  showNewScan = false,
}: ScanActionsProps): JSX.Element {
  return (
    <div className="grid grid-cols-1 gap-2">
      <Button type="button" onClick={onScanCode} disabled={disableCodeScan} className="h-10 text-xs font-semibold">
        {isScanning ? "Scanning..." : "Scan code"}
      </Button>
      <Button
        type="button"
        variant="secondary"
        onClick={onScanFile}
        disabled={disableFileScan}
        className="h-10 text-xs font-semibold"
      >
        {isScanning ? "Scanning..." : "Scan file"}
      </Button>
      {showNewScan ? (
        <Button
          type="button"
          variant="ghost"
          onClick={onNewScan}
          disabled={isScanning}
          className="h-10 text-xs font-semibold"
        >
          <RotateCcw className="h-4 w-4" />
          New Scan
        </Button>
      ) : null}
    </div>
  );
}
