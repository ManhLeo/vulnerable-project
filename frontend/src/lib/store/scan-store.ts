import { create } from "zustand";
import type { ScanCodeResultDto } from "@/types/api";

type ScanLanguage = "c" | "cpp";

interface ScanStoreState {
  code: string;
  language: ScanLanguage;
  latestResult: ScanCodeResultDto | null;
  selectedFindingIndex: number | null;
  hasTriggeredScan: boolean;
  
  setCode: (code: string) => void;
  setLanguage: (lang: ScanLanguage) => void;
  setLatestResult: (result: ScanCodeResultDto | null) => void;
  setSelectedFindingIndex: (index: number | null) => void;
  setHasTriggeredScan: (triggered: boolean) => void;
  prepareForNewScan: (keepLanguage?: boolean) => void;
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
  language: "cpp",
  latestResult: null,
  selectedFindingIndex: null,
  hasTriggeredScan: false,

  setCode: (code) => set({ code }),
  setLanguage: (language) => set({ language }),
  setLatestResult: (latestResult) => set({ latestResult }),
  setSelectedFindingIndex: (selectedFindingIndex) => set({ selectedFindingIndex }),
  setHasTriggeredScan: (hasTriggeredScan) => set({ hasTriggeredScan }),
  prepareForNewScan: (keepLanguage = true) => set((state) => ({
    code: "",
    language: keepLanguage ? state.language : "c",
    latestResult: null,
    selectedFindingIndex: null,
    hasTriggeredScan: false,
  })),
  resetWorkspace: () => set({
    code: "",
    language: "c",
    latestResult: null,
    selectedFindingIndex: null,
    hasTriggeredScan: false
  }),
}));
