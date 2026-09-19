import { useState } from "react";

export default function Land() {
  const [hidden, setHidden] = useState(true);

  return (
    <>
      <button
        onClick={() => setHidden(!hidden)}
        className="absolute z-10 right-[50%] px-5 pt-2 rounded-t-full bg-amber-50 transition-all"
        style={{
          bottom: hidden ? "0" : "33%",
        }}
      >
        land
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
