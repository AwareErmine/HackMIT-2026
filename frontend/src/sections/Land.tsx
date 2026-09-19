import { useState } from "react";
import { Menu } from "lucide-react";

export default function Land() {
  const [hidden, setHidden] = useState(true);

  return (
    <>
      <button
        onClick={() => setHidden(!hidden)}
        className="absolute left-[50%] z-10 px-10 pt-2 pb-1 rounded-t-full bg-amber-50 hover:opacity-80 transition-all"
        style={{
          bottom: hidden ? "0" : "33%",
          transform: "translate(-50%, 0)",
        }}
      >
        <Menu size={16} />
      </button>
      <div
        className="absolute z-1 bottom-0 w-screen h-[33%] transition-all bg-amber-50"
        style={{
          bottom: hidden ? "-33%" : "0",
        }}
      ></div>
    </>
  );
}
