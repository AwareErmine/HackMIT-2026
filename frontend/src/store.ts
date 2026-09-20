import { create } from "zustand";
import type { BackendFish } from "./api";

export type Fish = {
  volume: number; // range from 0-100 (percent from bottom)
  left: number; // pixels from the left edge
  id: string;
};

type State = {
  fishes: Fish[];
};

type Action = {
  setFishes: (f: Fish[]) => void;
  moveFish: (fid: Fish["id"], volume: number, left: number) => void;
  getFish: (fid: Fish["id"]) => Fish | undefined;
  syncFishies: (fishies: BackendFish[]) => void;
};

export const useFishStore = create<State & Action>((set, get) => ({
  fishes: [],
  setFishes: (fishes) => set({ fishes }),
  getFish: (fid) => get().fishes.find((f) => f.id == fid),
  moveFish: (fid, volume, left) => {
    set(({ fishes }) => {
      const fish = fishes.find((f) => f.id == fid);
      return {
        fishes: fish
          ? [
              ...fishes.filter((f) => f.id !== fid),
              {
                ...fish,
                volume: Math.max(0, Math.min(100, volume)),
                left: Math.max(0, Math.min(window.innerWidth - 80, left)),
              },
            ].sort((a, b) => a.id.localeCompare(b.id))
          : fishes,
      };
    });
  },
  syncFishies: (remoteFishies) =>
    set(({ fishes }) => ({
      fishes: remoteFishies
        .map((remote, index) => {
          const existing = fishes.find((fish) => fish.id === remote.id);
          return {
            ...remote,
            left:
              existing?.left ??
              ((index + 1) / (remoteFishies.length + 1)) *
                Math.max(0, window.innerWidth - 80),
          };
        })
        .sort((a, b) => a.id.localeCompare(b.id)),
    })),
}));
