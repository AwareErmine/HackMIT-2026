import { create } from "zustand";
import { putFish } from "./data";

export type Fish = {
  volume: number; // range from 0-100 (percent from bottom)
  left: number; // percent of screen from left
  id: string;
};

type State = {
  fishes: Fish[];
};

type Action = {
  setFishes: (f: Fish[]) => void;
  moveFish: (fid: Fish["id"], volume: number, left: number) => void;
  getFish: (fid: Fish["id"]) => Fish | undefined;
};

export const useFishStore = create<State & Action>((set, get) => ({
  fishes: [],
  setFishes: (f) => set(() => ({ fishes: f })),
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
                volume: volume < 100 ? volume : 100,
                left,
              },
            ].sort((a, b) => a.id.localeCompare(b.id))
          : fishes,
      };
    });

    putFish({ id: fid, volume, left });
  },
}));
