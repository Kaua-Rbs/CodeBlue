import { create } from "zustand";

interface UiState {
  selectedActionId: string | null;
  selectedWardId: string | null;
  traceOpen: boolean;
  traceActionId: string | null;
  setSelectedActionId: (actionId: string | null) => void;
  setSelectedWardId: (wardId: string | null) => void;
  openTrace: (actionId: string | null) => void;
  closeTrace: () => void;
}

export const useUiStore = create<UiState>((set) => ({
  selectedActionId: null,
  selectedWardId: null,
  traceOpen: false,
  traceActionId: null,
  setSelectedActionId: (selectedActionId) => set({ selectedActionId }),
  setSelectedWardId: (selectedWardId) => set({ selectedWardId }),
  openTrace: (traceActionId) => set({ traceOpen: true, traceActionId }),
  closeTrace: () => set({ traceOpen: false }),
}));
