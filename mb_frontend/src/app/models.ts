export interface MBEntry {
    easting: number
    northing: number
    h_depth: number
    zone_number: number
    zone_letter: string
    chunk_index: string
  }
  
export interface ProcessingSettings {
  filename: string
  sep: string
  to_utm: boolean
}

export interface ScriptSettings {
  stat_based: boolean,
  k_means: boolean,
  ml: boolean
  filename: string
}