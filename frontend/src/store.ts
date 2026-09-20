import { create } from "zustand";

export type Fish = {
  volume: number; // range from 0-100 (percent from bottom)
  left: number; // percent of screen from left
  id: string;
};

type State = {
  fishes: Fish[];
};

type Action = {
  addFish: (f: Fish) => void;
  removeFish: (fid: Fish["id"]) => void;
  moveFish: (fid: Fish["id"], volume: number, left: number) => void;
};

export const useFishStore = create<State & Action>((set) => ({
  fishes: [
    { volume: 10, id: "Anya", left: Math.random() * window.innerWidth * 0.8 },
    { volume: 10, id: "Aramie", left: Math.random() * window.innerWidth * 0.8 },
    { volume: 10, id: "Joyce", left: Math.random() * window.innerWidth * 0.8 },
    {
      volume: 10,
      id: "Rebecca",
      left: Math.random() * window.innerWidth * 0.8,
    },
  ],
  addFish: (f) =>
    set(({ fishes }) => ({
      fishes: [...fishes, f].sort((a, b) => a.id.localeCompare(b.id)),
    })),
  removeFish: (fid) =>
    set(({ fishes }) => ({
      fishes: fishes
        .filter((f) => f.id !== fid)
        .sort((a, b) => a.id.localeCompare(b.id)),
    })),
  moveFish: (fid, volume, left) =>
    set(({ fishes }) => {
      const fish = fishes.find((f) => f.id == fid);
      return {
        fishes: fish
          ? [
              ...fishes.filter((f) => f.id !== fid),
              {
                ...fish,
                volume,
                left,
              },
            ].sort((a, b) => a.id.localeCompare(b.id))
          : fishes,
      };
    }),
}));
