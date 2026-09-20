import { useEffect } from "react";
import Land from "./sections/Land";
import Water from "./sections/Water";
import Sky from "./sections/Sky";
import { useFishStore } from "./store";
import { getFishes } from "./data";

function App() {
  const setFishes = useFishStore((state) => state.setFishes);

  useEffect(() => {
    getFishes().then(setFishes);
  }, [setFishes]);

  return (
    <div className="overflow-clip h-screen relative">
      <Land />
      <div className="flex flex-col h-screen">
        <Sky className="flex-1 bg-sky-200" />
        <Water className="flex-5 bg-linear-to-b from-sky-300 to-sky-900" />
      </div>
    </div>
  );
}

export default App;
