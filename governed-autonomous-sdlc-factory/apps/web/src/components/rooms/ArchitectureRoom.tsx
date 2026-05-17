'use client';
import React from 'react';
import { ArchitectureIntelligence } from './ArchitectureIntelligence';

// ArchitectureRoom now delegates to ArchitectureIntelligence
export function ArchitectureRoom() {
  return <ArchitectureIntelligence />;
}
