import { create } from "zustand";

export type Fish = {
  volume: number; // range from 0-100 (percent from bottom)
  left?: number; // percent of screen from left
  id: string;
};

type State = {
  fishes: Fish[];
};

type Action = {
  addFish: (f: Fish) => void;
  removeFish: (fid: Fish["id"]) => void;
  setFishVolume: (fid: Fish["id"], volume: number) => void;
  setFishLeft: (fid: Fish["id"], left: number) => void;
};

export const useFishStore = create<State & Action>((set) => ({
  fishes: [
    { volume: 10, id: "Anya" },
    { volume: 10, id: "Aramie" },
    { volume: 10, id: "Joyce" },
    { volume: 10, id: "Rebecca" },
  ],
  addFish: (f) => set(({ fishes }) => ({ fishes: [...fishes, f] })),
  removeFish: (fid) =>
    set(({ fishes }) => ({ fishes: fishes.filter((f) => f.id !== fid) })),
  setFishVolume: (fid, volume) =>
    set(({ fishes }) => {
      const fish = fishes.find((f) => f.id == fid);
      return fish
        ? {
            fishes: [
              ...fishes.filter((f) => f.id !== fid),
              {
                ...fish,
                volume,
              },
            ],
          }
        : {};
    }),
  setFishLeft: (fid, left) =>
    set(({ fishes }) => {
      const fish = fishes.find((f) => f.id == fid);
      return fish
        ? {
            fishes: [
              ...fishes.filter((f) => f.id !== fid),
              {
                ...fish,
                left,
              },
            ],
          }
        : {};
    }),
}));
