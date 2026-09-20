import { useState } from "react";
import { Menu } from "lucide-react";
import { useFishStore } from "../store";
import { Slider } from "radix-ui";

const FishSlider = ({ fid }: { fid: string }) => {
  const moveFish = useFishStore((state) => state.moveFish);
  const fish = useFishStore((state) => state.fishes.find((f) => f.id == fid)!);
  return (
    <form>
      <Slider.Root
        className="flex items-center mx-[20%] gap-2"
        defaultValue={[fish.volume]}
        max={100}
        step={1}
        onValueChange={(val) => {
          moveFish(fid, val[0], fish.left);
        }}
      >
        <p>{Math.round(fish.volume)}</p>
        <div className="flex items-center grow relative">
          <Slider.Track className="relative grow bg-blue-950 h-1.75 rounded-full outline-1 outline-gray-300">
            <Slider.Range className="absolute bg-gray-300 h-1.75 rounded-l-full" />
          </Slider.Track>
          <Slider.Thumb
            className="block rounded-full h-6 focus:ring-2 ring-blue-950 aspect-square bg-gray-300 shadow-sm transition-colors"
            aria-label="Volume"
          />
        </div>
      </Slider.Root>
    </form>
  );
};

export default function Land() {
  const [hidden, setHidden] = useState(true);
  const fishes = useFishStore((state) => state.fishes);
  return (
    <>
      <button
        onClick={() => setHidden(!hidden)}
        className="absolute left-[50%] z-10 px-10 pt-2 pb-1 rounded-t-full bg-amber-100 hover:bg-gray-200 transition-all"
        style={{
          bottom: hidden ? "0" : "40%",
          transform: "translate(-50%, 0)",
        }}
      >
        <Menu size={16} />
      </button>
      <div
        className="absolute z-10 bottom-0 w-screen h-[40%] transition-all bg-amber-100"
        style={{
          bottom: hidden ? "-40%" : "0",
        }}
      >
        <div className="relative w-full h-full grid grid-cols-2 items-center">
          {fishes.map((fish, i) => (
            <FishSlider
              fid={fish.id}
              key={`fish-slider-${i}-${fish.id}-${fish.volume}`}
            />
          ))}
        </div>
      </div>
    </>
  );
}
