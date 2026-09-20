import { useEffect, useState } from "react";
import { Wifi, WifiOff } from "lucide-react";
import { getFishies } from "./api";
import Land from "./sections/Land";
import Water from "./sections/Water";
import Sky from "./sections/Sky";
import { useFishStore } from "./store";

function App() {
  const syncFishies = useFishStore((state) => state.syncFishies);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    const controller = new AbortController();

    const poll = async () => {
      try {
        syncFishies(await getFishies(controller.signal));
        setConnected(true);
      } catch {
        if (!controller.signal.aborted) setConnected(false);
      }
    };

    void poll();
    const interval = window.setInterval(poll, 1000);
    return () => {
      controller.abort();
      window.clearInterval(interval);
    };
  }, [syncFishies]);

  return (
    <div className="overflow-clip h-screen relative">
      <div
        className="absolute right-3 top-3 z-20 text-blue-950"
        title={connected ? "UNO Q connected" : "UNO Q disconnected"}
        aria-label={connected ? "UNO Q connected" : "UNO Q disconnected"}
      >
        {connected ? <Wifi size={20} /> : <WifiOff size={20} />}
      </div>
      <Land />
      <div className="flex flex-col h-screen">
        <Sky className="flex-1 bg-sky-200" />
        <Water className="flex-5 bg-linear-to-b from-sky-300 to-sky-900" />
      </div>
    </div>
  );
}

export default App;
