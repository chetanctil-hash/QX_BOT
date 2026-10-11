import { QuantScores } from '../types/portfolio';

export type Grade = 'A+' | 'A' | 'B' | 'C' | 'D' | 'F';

export const mapScoreToGrade = (score: number): Grade => {
  if (score >= 80) return 'A+';
  if (score >= 70) return 'A';
  if (score >= 60) return 'B';
  if (score >= 50) return 'C';
  if (score >= 40) return 'D';
  return 'F';
};

export const formatMomentumLabel = (val: number): string => {
  if (val >= 80) return 'CONFIRMED';
  if (val >= 60) return 'STRENGTHENING';
  if (val >= 40) return 'NEUTRAL';
  return 'WEAKENING';
};

export const getQXColor = (score: number): string => {
  if (score >= 80) return 'text-qx-green';
  if (score >= 60) return 'text-qx-blue';
  if (score >= 40) return 'text-qx-yellow';
  return 'text-qx-red';
};
