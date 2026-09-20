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
        className="relative flex items-center"
        defaultValue={[fish.volume]}
        max={100}
        step={1}
        onValueChange={(val) => {
          moveFish(fid, val[0], fish.left);
        }}
      >
        <Slider.Track className="relative grow bg-gray-500 h-5">
          <Slider.Range className="absolute bg-black h-5" />
        </Slider.Track>
        <Slider.Thumb
          className="block rounded-full h-10 aspect-square bg-blue-500"
          aria-label="Volume"
        />
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
        className="absolute left-[50%] z-10 px-10 pt-2 pb-1 rounded-t-full bg-amber-100 hover:opacity-80 transition-all"
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
        <div className="relative w-full h-full grid grid-cols-2">
          {fishes
            .sort((a, b) => a.id.localeCompare(b.id))
            .map((fish, i) => (
              <FishSlider fid={fish.id} key={`fish-slider-${i}-${fish.id}`} />
            ))}
        </div>
      </div>
    </>
  );
}
