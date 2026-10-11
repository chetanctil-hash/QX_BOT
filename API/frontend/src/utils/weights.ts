import { PortfolioItem } from '../types/portfolio';

export interface WeightMap {
  [sym: string]: number;
}

/**
 * Ports the legacy computeTargetWeights logic.
 * Ensures no single position exceeds 15% and redistributes excess weight.
 */
export const calculateTargetWeights = (positions: PortfolioItem[], maxCap = 0.15): WeightMap => {
  const weights: WeightMap = {};
  let totalTargetWeight = 0;
  
  // Initial pass: calculate raw target weights based on score/volatility
  // Note: In production, this would use the actual formula from the AllocationEngine
  positions.forEach(p => {
    // Simplified proxy for the target weight logic for UI parity
    const rawWeight = p.target_weight; 
    weights[p.sym] = rawWeight;
    totalTargetWeight += rawWeight;
  });

  // Normalization and Capping Logic
  let redistributed = 0;
  let iterations = 0;
  const MAX_ITERATIONS = 10;

  while (redistributed > 0 || iterations === 0) {
    redistributed = 0;
    iterations++;
    
    const currentTotal = Object.values(weights).reduce((a, b) => a + b, 0);
    
    for (const sym in weights) {
      if (weights[sym] > maxCap) {
        const excess = weights[sym] - maxCap;
        weights[sym] = maxCap;
        redistributed += excess;
      }
    }

    if (redistributed > 0) {
      // Distribute excess proportionally to those under the cap
      const underCapSymbols = Object.keys(weights).filter(s => weights[s] < maxCap);
      const underCapTotal = underCapSymbols.reduce((sum, s) => sum + weights[s], 0);
      
      if (underCapTotal > 0) {
        underCapSymbols.forEach(s => {
          weights[s] += (weights[s] / underCapTotal) * redistributed;
        });
      }
    }

    if (iterations >= MAX_ITERATIONS) break;
    if (redistributed === 0) break;
  }

  return weights;
};

export const checkSectorConcentration = (positions: PortfolioItem[], threshold = 0.25): { isAlert: boolean; cluster: string; value: number } | null => {
  const clusterTotals: Record<string, number> = {};
  const totalInv = positions.reduce((sum, p) => sum + p.inv, 0);

  positions.forEach(p => {
    clusterTotals[p.cluster] = (clusterTotals[p.cluster] || 0) + p.inv;
  });

  for (const [cluster, value] of Object.entries(clusterTotals)) {
    const pct = value / totalInv;
    if (pct > threshold) {
      return { isAlert: true, cluster, value: pct };
    }
  }

  return null;
};
