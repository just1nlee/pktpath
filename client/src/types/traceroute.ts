export interface GeolocationData {
  latitude: number | null;
  longitude: number | null;
  country: string | null;
  country_code: string | null;
  city: string | null;
  region: string | null;
  postal_code: string | null;
  timezone: string | null;
  isp: string | null;
  source: string;
}

export interface TracerouteHop {
  hop: number;
  ip: string;
  times: number[];
  hostname: string | null;
  geolocation: GeolocationData;
  lat: number | null;
  lng: number | null;
}

export interface TracerouteResponse {
  target: string;
  hops: TracerouteHop[];
}
