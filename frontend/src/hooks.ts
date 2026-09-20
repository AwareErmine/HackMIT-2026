import React from "react";

const useMousePosition = () => {
  const [mousePosition, setMousePosition] = React.useState({
    x: null,
    y: null,
  });

  React.useEffect(() => {
    const updateMousePosition = (ev) => {
      setMousePosition({ x: ev.clientX, y: ev.clientY });
    };
    window.addEventListener("dragover", updateMousePosition);
    return () => {
      window.removeEventListener("dragover", updateMousePosition);
    };
  }, []);

  return mousePosition;
};

export default useMousePosition;
