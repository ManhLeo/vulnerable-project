"use client";

import { Button } from "@/components/ui/button";

interface ScanActionsProps {
  onScanCode: () => void;
  onScanFile: () => void;
  disableCodeScan: boolean;
  disableFileScan: boolean;
  isScanning: boolean;
}

export function ScanActions({
  onScanCode,
  onScanFile,
  disableCodeScan,
  disableFileScan,
  isScanning,
}: ScanActionsProps): JSX.Element {
  return (
    <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
      <Button type="button" onClick={onScanCode} disabled={disableCodeScan} className="h-9 text-xs font-semibold">
        {isScanning ? "Scanning..." : "Scan code"}
      </Button>
      <Button
        type="button"
        variant="secondary"
        onClick={onScanFile}
        disabled={disableFileScan}
        className="h-9 text-xs font-semibold"
      >
        {isScanning ? "Scanning..." : "Scan file"}
      </Button>
    </div>
  );
}
