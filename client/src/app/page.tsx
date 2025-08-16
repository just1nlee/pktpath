"use client";

import dynamic from 'next/dynamic';
import type { Position } from "@/components/globe";
import { useState, useMemo } from 'react';
import { GlobeConfig } from "@/components/globe";
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"


// Dynamically import the globe component with SSR disabled
const World = dynamic(() => import("@/components/globe").then(mod => ({ default: mod.World })), {
  ssr: false,
  loading: () => (
    <div className="flex items-center justify-center h-full">
      <div className="text-white text-lg">Loading 3D Globe...</div>
    </div>
  )
});

const GLOBE_CONFIG = {
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

export default function Home() {
  const [target, setTarget] = useState("");
  const [tracerouteData, setTracerouteData] = useState<Position[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async () => {
    // Check user input
    if (!target.trim()) {
      setError("Please enter a target");
      return;
    }

    // Set loading state
    setIsLoading(true);
    setError(null);

    // Make API request to backend
    try {
      const response = await fetch("http://localhost:8000/api/v1/traceroute/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ target: target.trim() }),
      });
      const data = await response.json();

      // Verify response
      if (!response.ok) {
        throw new Error(data.detail || "Failed to run traceroute");
      }
      if (!data.success) {
        throw new Error(data.error || "Traceroute failed");
      }

      // Format data for GitGlobe
      const positions: Position[] = data.hops
      .filter((hop: any) => hop.lat && hop.lng)
      .map((hop: any, index: number) => ({
        order: index,
        startLat: hop.lat,
        startLng: hop.lng,
        endLat: hop.lat,
        endLng: hop.lng,
        arcAlt: 0.1,
        color: '#ff6b6b'
      }));

      // Update state
      setTracerouteData(positions);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      setTracerouteData([]);
      // Revert loading state
    } finally {
      setIsLoading(false);
    }
  };

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
          <World globeConfig={GLOBE_CONFIG} data={tracerouteData} />
        </div>
        <div className="flex w-full max-w-sm items-center gap-2">
          <Input 
            placeholder="Enter a domain or IP address" 
            value={target}
            onChange={(e) => setTarget(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSubmit()}
          />
          <Button 
            onClick={handleSubmit}
            disabled={isLoading}
            variant="outline"
          >
            {isLoading ? 'Running...' : 'Submit'}
          </Button>
          {error && (
            <div className="text-center mt-4">
              <p className="text-red-400 text-sm">{error}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}