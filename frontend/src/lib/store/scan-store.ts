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

const DEFAULT_CODE = `#include <iostream>
#include <cstring>

void unsafe_copy(const char* src) {
    char dest[16];
    // Potential buffer overflow
    strcpy(dest, src);
    std::cout << dest << std::endl;
}

int main() {
    unsafe_copy("Hello World!");
    return 0;
}
`;

export const useScanStore = create<ScanStoreState>((set) => ({
  code: DEFAULT_CODE,
  language: "c_cpp",
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
    language: "c_cpp",
    latestResult: null,
    selectedFindingIndex: null,
    hasTriggeredScan: false
  }),
}));
