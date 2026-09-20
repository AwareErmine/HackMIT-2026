type SkyProps = {
  className?: string;
};

export default function Sky({ className }: SkyProps) {
  return (
    <div className={className}>
      <div className="p-10 h-full w-full flex items-center">
        <h1 className="font-modak text-5xl text-shadow-md text-white">
          BlubBlub
        </h1>
      </div>
    </div>
  );
}
