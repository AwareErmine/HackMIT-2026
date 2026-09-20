import { useFishStore } from "../store";
import { useEffect, useState, type Ref } from "react";
import { useDrag, useDrop } from "react-dnd";
import { fishGifs, fishPngs } from "../images";
import { getEmptyImage } from "react-dnd-html5-backend";
import { putFishVolume } from "../api";

type mousePositionType = { x: null | number; y: null | number };

function Fish({
  id,
  idx,
  mousePosition,
}: {
  id: string;
  idx: number;
  mousePosition: mousePositionType;
}) {
  const { left, volume } = useFishStore((state) =>
    state.fishes.find((f) => f.id == id),
  )!;
  const [{ isDragging }, drag, preview] = useDrag(() => ({
    type: "fish",
    item: { id },
    collect: (monitor) => ({
      isDragging: !!monitor.isDragging(),
    }),
  }));

  useEffect(() => {
    preview(getEmptyImage(), { captureDraggingState: true });
  }, [preview]);

  return isDragging ? (
    <div
      style={{
        top: `${mousePosition.y}px`,
        left: `${mousePosition.x}px`,
        transform: "translate(-50%, -50%)",
      }}
      className="fixed"
    >
      <img className="w-20" src={fishGifs[idx % fishGifs.length]} />
    </div>
  ) : (
    <div
      ref={drag as unknown as Ref<HTMLDivElement>}
      style={{
        top: `${100 - volume}%`,
        left: `${left}px`,
        opacity: isDragging ? "0%" : "100%",
      }}
      className="absolute"
    >
      <img className="w-20" src={fishPngs[idx % fishPngs.length]} />
    </div>
  );
}

export default function Fishes() {
  const fishes = useFishStore((state) => state.fishes);
  const moveFish = useFishStore((state) => state.moveFish);
  const [mousePosition, setMousePosition] = useState<mousePositionType>({
    x: null,
    y: null,
  });
  const [, drop] = useDrop(
    () => ({
      accept: "fish",
      drop: (item: { id: string }, monitor) => {
        const delta = monitor.getDifferenceFromInitialOffset()!;
        const { left, volume } = fishes.find((f) => f.id == item.id)!;
        const newLeft = delta.x + (left ?? 0);
        const topPercentDiff = (delta.y / window.innerHeight) * 100;
        const newVolume = Math.max(0, Math.min(100, volume - topPercentDiff));
        moveFish(item.id, newVolume, newLeft);
        void putFishVolume(item.id, newVolume).catch(() => undefined);
      },
    }),
    [fishes],
  );
  return (
    <div
      ref={drop as unknown as Ref<HTMLDivElement>}
      className="relative w-full h-full overflow-clip"
      onMouseOver={(ev) => setMousePosition({ x: ev.clientX, y: ev.clientY })}
      onDragOver={(ev) => setMousePosition({ x: ev.clientX, y: ev.clientY })}
    >
      {fishes.map((f, i) => (
        <Fish id={f.id} key={f.id} idx={i} mousePosition={mousePosition} />
      ))}
    </div>
  );
}
