from fastapi import APIRouter
from typing import Dict
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.ai.mega_intelligence import MegaIntelligenceSystem, PerformanceBreakthroughs

router = APIRouter(prefix="/api/mega", tags=["mega_intelligence"])

@router.get("/intelligence")
async def get_total_intelligence():
    return MegaIntelligenceSystem.get_total_intelligence()

@router.get("/architectures")
async def get_model_architectures():
    return MegaIntelligenceSystem.revolutionary_model_architectures()

@router.get("/speed")
async def get_speed_innovations():
    return MegaIntelligenceSystem.ultra_speed_innovations()

@router.get("/learning")
async def get_learning_systems():
    return MegaIntelligenceSystem.advanced_learning_systems()

@router.get("/reality")
async def get_reality_manipulation():
    return MegaIntelligenceSystem.reality_manipulation()

@router.get("/consciousness")
async def get_consciousness_innovations():
    return MegaIntelligenceSystem.consciousness_innovations()

@router.get("/creativity")
async def get_creative_innovations():
    return MegaIntelligenceSystem.creative_innovations()

@router.get("/optimization")
async def get_optimization_breakthroughs():
    return MegaIntelligenceSystem.optimization_breakthroughs()

@router.get("/prediction")
async def get_prediction_systems():
    return MegaIntelligenceSystem.prediction_systems()

@router.get("/communication")
async def get_communication_systems():
    return MegaIntelligenceSystem.communication_systems()

@router.get("/integration")
async def get_integration_perfection():
    return MegaIntelligenceSystem.integration_perfection()

@router.get("/performance/speed")
async def get_speed_records():
    return PerformanceBreakthroughs.speed_records()

@router.get("/performance/accuracy")
async def get_accuracy_records():
    return PerformanceBreakthroughs.accuracy_records()

@router.get("/performance/efficiency")
async def get_efficiency_records():
    return PerformanceBreakthroughs.efficiency_records()

@router.get("/performance/scalability")
async def get_scalability_records():
    return PerformanceBreakthroughs.scalability_records()
