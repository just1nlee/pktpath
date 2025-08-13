"use client";

import dynamic from 'next/dynamic';
import type { Position } from "@/components/globe";

// Dynamically import the globe component with SSR disabled
const World = dynamic(() => import("@/components/globe").then(mod => ({ default: mod.World })), {
  ssr: false,
  loading: () => (
    <div className="flex items-center justify-center h-full">
      <div className="text-white text-lg">Loading 3D Globe...</div>
    </div>
  )
});

export default function Home() {
  const globeConfig = {
    globeColor: "#1d072e",
    showAtmosphere: true,
    atmosphereColor: "#ffffff",
    atmosphereAltitude: 0.1,
    polygonColor: "rgba(255,255,255,0.7)",
    ambientLight: "#ffffff",
    directionalLeftLight: "#ffffff",
    directionalTopLight: "#ffffff",
    pointLight: "#ffffff",
    autoRotate: true,
    autoRotateSpeed: 1,
  };

  // Empty data array for now - just showing the globe
  const sampleData: Position[] = [];

  return (
    <div className="min-h-screen bg-black">
      <div className="max-w-6xl mx-auto p-8">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">
            PktPath
          </h1>
          <p className="text-lg text-gray-300">
            Visualize your packet's journey across the internet
          </p>
        </div>

        <div className="w-full h-[600px]">
          <World globeConfig={globeConfig} data={sampleData} />
        </div>

        <div className="text-center mt-8">
          <p className="text-gray-400">
            A beautiful 3D globe ready for traceroute visualization
          </p>
        </div>
      </div>
    </div>
  );
}