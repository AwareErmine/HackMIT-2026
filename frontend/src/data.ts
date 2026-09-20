import type { Fish } from "./store";

const URL = "http://localhost:5005/fishies";

export const getFishes = () =>
  fetch(URL, {
    method: "GET",
  })
    .then((res) => res.json())
    .then((json: Omit<Fish, "left">[]) =>
      json.map((j) => ({ ...j, left: Math.random() * 100 })),
    );

export const putFish = (fish: Fish) =>
  fetch(URL, {
    method: "PUT",
    body: JSON.stringify(fish),
  });
