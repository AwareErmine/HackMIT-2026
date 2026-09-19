type LandProps = {
  className?: string;
};

export default function Land({ className }: LandProps) {
  return <div className={className}></div>;
}
