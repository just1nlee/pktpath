"use client";

import dynamic from 'next/dynamic';
import React, { useEffect } from "react";
import { motion } from "motion/react";
import type { Position } from "@/components/ui/globe";
import { useState, useMemo, useCallback } from 'react';
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"

// Move dynamic import completely outside (no hooks here)
const World = dynamic(() => import("@/components/ui/globe").then(mod => ({ default: mod.World })), {
  ssr: false,
  loading: () => (
    <div className="flex items-center justify-center h-full">
      <div className="text-white text-lg">Loading 3D Globe...</div>
    </div>
  )
});

// Create a memoized wrapper component outside
const MemoizedWorld = React.memo(({ globeConfig, data }: { globeConfig: any, data: Position[] }) => {
  return <World globeConfig={globeConfig} data={data} />;
});

MemoizedWorld.displayName = 'MemoizedWorld';

export default function Home() {
  const [target, setTarget] = useState("");
  const [tracerouteData, setTracerouteData] = useState<Position[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [userLocation, setUserLocation] = useState({ lat: 45.4871, lng: -122.8033 }); // Default

  // Memoize the globe configuration to prevent unnecessary re-renders
  const memoizedGlobeConfig = useMemo(() => ({}), []);

  // Get user location on component mount
  useEffect(() => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const newLocation = {
            lat: position.coords.latitude,
            lng: position.coords.longitude
          };
          // Only update if location actually changed
          setUserLocation(prevLocation => {
            if (prevLocation.lat !== newLocation.lat || prevLocation.lng !== newLocation.lng) {
              return newLocation;
            }
            return prevLocation;
          });
        },
        (error) => {
          console.log("Geolocation error:", error);
          // Keep default location
        }
      );
    }
  }, []);



  const handleSubmit = useCallback(async (inputValue?: string) => {
    // Use provided input value or fall back to target state
    const currentTarget = inputValue || target;
    
    // Check user input
    if (!currentTarget.trim()) {
      setError("Please enter a target");
      return;
    }

    // Set loading state
    setIsLoading(true);
    setError(null);

    try {
      // Make API request to backend
      const response = await fetch("http://localhost:8000/api/v1/traceroute/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ target: currentTarget.trim() }),
      });

      // Check if response is ok
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
      }

      // Parse the JSON response
      const data = await response.json();
      console.log("Raw API response:", data); // Debug log

      // Validate the response structure
      if (!data.hops || !Array.isArray(data.hops)) {
        throw new Error("Invalid response format: missing or invalid hops array");
      }

      // Parse and filter hops with valid coordinates
      const validHops = data.hops.filter((hop: any) => {
        // Check if hop has valid coordinates
        const hasValidCoords = hop.lat !== null && hop.lng !== null && 
                             !isNaN(hop.lat) && !isNaN(hop.lng);
        
        if (!hasValidCoords) {
          console.log(`Skipping hop ${hop.hop}: ${hop.ip} - no valid coordinates`);
        }
        
        return hasValidCoords;
      });

      console.log(`Found ${validHops.length} hops with valid coordinates out of ${data.hops.length} total hops`);

      // Format data for the globe with connected path and different colors
      const positions: Position[] = [];
      
      // Add your starting location (customize this to your location)
      const startLocation = userLocation;
      
      // Create arcs connecting all points in sequence
      for (let i = 0; i < validHops.length; i++) {
        const hop = validHops[i];
        const colors = ["#E4DBA0", "#E5BB63", "#E07432"];
        
        if (i === 0) {
          // First arc: from start location to first hop
          positions.push({
            order: i,
            startLat: startLocation.lat,
            startLng: startLocation.lng,
            endLat: hop.lat,
            endLng: hop.lng,
            arcAlt: 0.1,
            color: colors[Math.floor(Math.random() * (colors.length - 1))],

          });
        } else {
          // Subsequent arcs: from previous hop to current hop
          const previousHop = validHops[i - 1];
          positions.push({
            order: i,
            startLat: previousHop.lat,
            startLng: previousHop.lng,
            endLat: hop.lat,
            endLng: hop.lng,
            arcAlt: 0.1,
            color: colors[Math.floor(Math.random() * (colors.length - 1))],

          });
        }
      }

      console.log("Formatted positions for globe:", positions); // Debug log

      // Update state
      setTracerouteData(positions);
      
      // Clear the input field after successful submission
      setTarget("");
      
      // Show success message
      if (validHops.length === 0) {
        setError("No hops with valid coordinates found. Try a different target.");
      } else {
        setError(null);
      }

    } catch (err) {
      console.error("Error parsing traceroute response:", err);
      setError(err instanceof Error ? err.message : 'An error occurred');
      setTracerouteData([]);
    } finally {
      setIsLoading(false);
    }
  }, [userLocation]);

  // Memoize the input change handler
  const handleInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    setTarget(e.target.value);
  }, []);

  // Memoize the key down handler
  const handleKeyDown = useCallback((e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      handleSubmit(e.currentTarget.value);
    }
  }, [handleSubmit]);

  return (
    <div className="min-h-screen bg-black">
      <div className="max-w-6xl mx-auto p-8">

        {/* Globe container with fixed aspect ratio to prevent shape distortion */}
        <div className="relative w-full mb-4" style={{ aspectRatio: '1/1', maxHeight: '600px' }} data-globe-container>
          <div className="absolute inset-0">
            <MemoizedWorld 
              globeConfig={memoizedGlobeConfig} 
              data={tracerouteData} 
            />
          </div>
        </div>
        
        {/* Input section */}
        <div className="flex flex-col items-center gap-4">
          <div className="flex w-full max-w-sm items-center gap-2">
            <Input 
              type="text"
              placeholder="Enter a domain or IP address" 
              value={target}
              onChange={handleInputChange}
              onKeyDown={handleKeyDown}
              className="flex-1 text-white"
            />
            <Button 
              onClick={() => handleSubmit()}
              disabled={isLoading}
              variant="outline"
              className="whitespace-nowrap"
            >
              {isLoading ? 'Running...' : 'Submit'}
            </Button>
          </div>
          
          {error && (
            <div className="text-center">
              <p className="text-red-400 text-sm">{error}</p>
            </div>
          )}
        </div>
        
        {/* IP2Location LITE Attribution */}
        <div className="mt-8 text-center">
          <p className="text-xs text-gray-500">
            pktpath uses the{" "}
            <a 
              href="https://lite.ip2location.com" 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-gray-400 hover:text-gray-300 underline"
            >
              IP2Location LITE database
            </a>{" "}
            for IP geolocation
          </p>
        </div>
      </div>
    </div>
  );
}