import { useEffect } from "react";
import Land from "./sections/Land";
import Water from "./sections/Water";
import Sky from "./sections/Sky";

function App() {
  useEffect(() => {
    // TODO: connect to socket server!
  });

  return (
    <div>
      <Land />
      <div className="flex flex-col h-screen">
        <Sky className="flex-2 bg-sky-200 " />
        <Water className="flex-3 bg-linear-to-b from-sky-300 to-sky-900" />
      </div>
    </div>
  );
}

export default App;
