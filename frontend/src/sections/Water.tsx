import Fishes from "./Fishes";

type WaterProps = {
  className?: string;
};

export default function Water({ className }: WaterProps) {
  return (
    <div className={className + " relative"}>
      <Fishes />
    </div>
  );
}
