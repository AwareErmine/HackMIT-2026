import { useFishStore } from "../store";
import { type Ref } from "react";
import { useDrag, useDrop } from "react-dnd";

function Fish({ id }: { id: string }) {
  const { left, volume } = useFishStore((state) =>
    state.fishes.find((f) => f.id == id),
  )!;
  const [, drag] = useDrag(() => ({
    type: "fish",
    item: { id },
  }));
  return (
    <div
      ref={drag as unknown as Ref<HTMLDivElement>}
      style={{ bottom: `${volume}%`, left: `${left}px` }}
      className="absolute h-20 aspect-square bg-yellow-300 rounded-full opacity-70"
    ></div>
  );
}

export default function Fishes() {
  const fishes = useFishStore((state) => state.fishes);
  const moveFish = useFishStore((state) => state.moveFish);
  const [, drop] = useDrop(
    () => ({
      accept: "fish",
      drop: (item: { id: string }, monitor) => {
        const delta = monitor.getDifferenceFromInitialOffset()!;
        const { left, volume } = fishes.find((f) => f.id == item.id)!;
        const newLeft = delta.x + (left ?? 0);
        const topPercentDiff = (delta.y / window.innerHeight) * 100;
        const newVolume = volume - topPercentDiff;
        moveFish(item.id, newVolume, newLeft);
      },
    }),
    [fishes],
  );
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
