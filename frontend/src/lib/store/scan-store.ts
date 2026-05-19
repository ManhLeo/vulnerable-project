import { create } from "zustand";
import type { ScanCodeResultDto } from "@/types/api";

interface ScanStoreState {
  code: string;
  language: string;
  latestResult: ScanCodeResultDto | null;
  selectedFindingIndex: number | null;
  hasTriggeredScan: boolean;
  
  setCode: (code: string) => void;
  setLanguage: (lang: string) => void;
  setLatestResult: (result: ScanCodeResultDto | null) => void;
  setSelectedFindingIndex: (index: number | null) => void;
  setHasTriggeredScan: (triggered: boolean) => void;
  resetWorkspace: () => void;
}

const DEFAULT_CODE = `def hello(name: str) -> str:
    return f"Hello, {name}"
`;

export const useScanStore = create<ScanStoreState>((set) => ({
  code: DEFAULT_CODE,
  language: "py",
  latestResult: null,
  selectedFindingIndex: null,
  hasTriggeredScan: false,

  setCode: (code) => set({ code }),
  setLanguage: (language) => set({ language }),
  setLatestResult: (latestResult) => set({ latestResult }),
  setSelectedFindingIndex: (selectedFindingIndex) => set({ selectedFindingIndex }),
  setHasTriggeredScan: (hasTriggeredScan) => set({ hasTriggeredScan }),
  resetWorkspace: () => set({
    code: DEFAULT_CODE,
    language: "py",
    latestResult: null,
    selectedFindingIndex: null,
    hasTriggeredScan: false
  }),
}));
