import { useFishStore } from "../store";
import type { Fish as FishProps } from "../store";
import { useState, type Ref } from "react";
import { useDrag, useDrop } from "react-dnd";

function Fish({ id }: { id: string }) {
  const [randomFallBack] = useState(() => Math.random() * 100);
  const { left, volume } = useFishStore((state) =>
    state.fishes.find((f) => f.id == id),
  ) as FishProps;
  const [, drag] = useDrag(() => ({
    type: "fish",
    item: { id, left: left ?? randomFallBack, volume } as FishProps,
  }));
  return (
    <div
      ref={drag as unknown as Ref<HTMLDivElement>}
      style={{ bottom: `${volume}%`, left: `${left ?? randomFallBack}%` }}
      className="absolute h-20 aspect-square bg-yellow-300 rounded-full opacity-70"
    ></div>
  );
}

export default function Fishes() {
  const fishes = useFishStore((state) => state.fishes);
  const setFishVolume = useFishStore((state) => state.setFishVolume);
  const setFishLeft = useFishStore((state) => state.setFishLeft);
  const [, drop] = useDrop(() => ({
    accept: "fish",
    drop: (item: FishProps, monitor) => {
      const pos = monitor.getDifferenceFromInitialOffset();
      if (pos) {
        const leftPercent = (pos.x / window.innerWidth) * 100;
        setFishLeft(item.id, (item.left ?? 0) + leftPercent);

        const topPercent = (pos.y / window.innerHeight) * 100;
        setFishVolume(item.id, item.volume - topPercent);
      }
    },
  }));
  return (
    <div
      ref={drop as unknown as Ref<HTMLDivElement>}
      className="z-1 h-screen w-screen absolute overflow-clip"
    >
      {fishes.map((f) => (
        <Fish id={f.id} key={f.id} />
      ))}
    </div>
  );
}
