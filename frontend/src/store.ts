import { create } from "zustand";

type Fish = {
  volume: number; // range from 0-100
  id: string;
};

type State = {
  fishes: Fish[];
};

type Action = {
  addFish: (f: Fish) => void;
  removeFish: (f: Fish["id"]) => void;
};

export const useFishStore = create<State & Action>((set) => ({
  addFish: (f) => set(({ fishes }) => ({ fishes: [...fishes, f] })),
  removeFish: (fid) =>
    set(({ fishes }) => ({ fishes: fishes.filter((f) => f.id !== fid) })),
  fishes: [],
}));
