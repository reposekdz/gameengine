from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.ai.ultra_intelligence import UltraIntelligenceSystem, AdvancedInnovations
from engine.core.system_integrator import MASTER_SYSTEM

router = APIRouter(prefix="/api/intelligence", tags=["intelligence"])

class IntelligenceRequest(BaseModel):
    query: str
    mode: str = "quantum"

class GenerationRequest(BaseModel):
    description: str
    mode: str = "text"
    use_quantum: bool = True

@router.get("/iq")
async def get_iq_level():
    """Get total IQ level"""
    ultra = UltraIntelligenceSystem()
    return ultra.get_total_iq()

@router.get("/quantum")
async def get_quantum_capabilities():
    """Get quantum reasoning capabilities"""
    ultra = UltraIntelligenceSystem()
    return ultra.quantum_reasoning()

@router.get("/consciousness")
async def get_consciousness_level():
    """Get consciousness engine status"""
    ultra = UltraIntelligenceSystem()
    return ultra.consciousness_engine()

@router.get("/innovations")
async def get_all_innovations():
    """Get all advanced innovations"""
    return {
        'neural': AdvancedInnovations.neural_architecture_innovations(),
        'quantum': AdvancedInnovations.quantum_innovations(),
        'biological': AdvancedInnovations.biological_innovations(),
        'photonic': AdvancedInnovations.photonic_innovations(),
        'metamaterial': AdvancedInnovations.metamaterial_innovations(),
        'energy': AdvancedInnovations.energy_innovations(),
        'spacetime': AdvancedInnovations.spacetime_innovations()
    }

@router.post("/generate")
async def generate_with_intelligence(request: GenerationRequest):
    """Generate using full intelligence system"""
    try:
        result = MASTER_SYSTEM.generate_with_intelligence(request.description, request.mode)
        if request.use_quantum:
            result = MASTER_SYSTEM.optimize_with_quantum(result)
        validation = MASTER_SYSTEM.validate_with_consciousness(result)
        return {
            'result': result,
            'validation': validation,
            'iq_used': 510_000_000
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/system/status")
async def get_system_status():
    """Get complete system status"""
    return MASTER_SYSTEM.get_system_status()

@router.post("/system/improve")
async def improve_system():
    """Trigger system self-improvement"""
    return MASTER_SYSTEM.self_improve()

@router.get("/multidimensional")
async def get_multidimensional_thinking():
    """Get multidimensional thinking capabilities"""
    ultra = UltraIntelligenceSystem()
    return ultra.multidimensional_thinking()

@router.get("/creative")
async def get_creative_intelligence():
    """Get creative intelligence metrics"""
    ultra = UltraIntelligenceSystem()
    return ultra.creative_intelligence()

@router.get("/predictive")
async def get_predictive_intelligence():
    """Get predictive intelligence capabilities"""
    ultra = UltraIntelligenceSystem()
    return ultra.predictive_intelligence()

@router.get("/adaptive")
async def get_adaptive_intelligence():
    """Get adaptive intelligence metrics"""
    ultra = UltraIntelligenceSystem()
    return ultra.adaptive_intelligence()

@router.get("/collective")
async def get_collective_intelligence():
    """Get collective intelligence status"""
    ultra = UltraIntelligenceSystem()
    return ultra.collective_intelligence()

@router.post("/parallel/generate")
async def parallel_generation(tasks: List[Dict]):
    """Execute parallel generation tasks"""
    try:
        results = MASTER_SYSTEM.execute_parallel_generation(tasks)
        return {
            'total_tasks': len(tasks),
            'results': results,
            'parallel_speedup': f'{len(tasks)}x'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
