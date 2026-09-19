import { useFishStore } from "../store";
import type { Fish as FishProps } from "../store";
import { useState, type Ref } from "react";
import { useDrag, useDrop } from "react-dnd";

function Fish({ volume, id, left }: FishProps) {
  const [randomFallBack] = useState(() => Math.random() * 100);
  const [collected, drag, dragPreview] = useDrag(() => ({
    type: "fish",
    item: { id, left, volume } as FishProps,
  }));
  return (
    <div
      ref={drag as unknown as Ref<HTMLDivElement>}
      style={{ bottom: `${volume}%`, left: `${left ?? randomFallBack}%` }}
      className="absolute h-10 aspect-square bg-yellow-300 rounded-full opacity-70"
    ></div>
  );
}

export default function Fishes() {
  const fishes = useFishStore((state) => state.fishes);
  const setFishVolume = useFishStore((state) => state.setFishVolume);
  const setFishLeft = useFishStore((state) => state.setFishLeft);
  const [collectedProps, drop] = useDrop(() => ({
    accept: "fish",
    drop: (item: FishProps, monitor) => {
      const delta = monitor.getDifferenceFromInitialOffset();
      if (delta) {
        const leftPercent = Math.round((delta.x / window.innerWidth) * 100);
        const topPercent = Math.round((delta.y / window.innerHeight) * 100);
        const left = Math.round(item.left ?? 0 + leftPercent);
        const volume = Math.round(item.volume - topPercent); // delta is from the top
        console.log(left, volume);
        setFishVolume(item.id, volume);
        setFishLeft(item.id, left);
      }
    },
  }));
  return (
    <div
      ref={drop as unknown as Ref<HTMLDivElement>}
      className="z-1 h-screen w-screen absolute"
    >
      {fishes.map((f) => (
        <Fish {...f} key={f.id} />
      ))}
    </div>
  );
}
