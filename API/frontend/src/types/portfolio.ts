export type MarketRegime = 'BULLISH' | 'BEARISH' | 'NEUTRAL';

export interface RegimeData {
  regime: MarketRegime;
  benchmark_price: number;
  sma200: number;
}

export interface QuantScores {
  mom: number;
  earnings: number;
  entry: number;
  composite: number;
}

export interface PortfolioItem {
  sym: string;
  name: string;
  cluster: string;
  qty: number;
  avg: number;
  ltp: number;
  inv: number;
  pl: number;
  ret: number;
  volatility: number;
  target_weight: number;
  scores: QuantScores;
}

export interface SectorAlert {
  isAlert: boolean;
  cluster: string;
  percentage: number;
}
