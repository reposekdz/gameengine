from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import Optional
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.auth.auth_manager import AuthManager
from engine.payments.payment_processor import PaymentProcessor

router = APIRouter(prefix="/api/auth", tags=["authentication"])

auth_manager = AuthManager()
payment_processor = PaymentProcessor()

class RegisterRequest(BaseModel):
    email: str
    password: str
    full_name: str

class LoginRequest(BaseModel):
    email: str
    password: str

class SubscriptionRequest(BaseModel):
    plan_type: str
    payment_method_id: str

class PayPerUseRequest(BaseModel):
    item_type: str
    item_id: str
    price: float

def get_current_user(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith('Bearer '):
        raise HTTPException(status_code=401, detail='Not authenticated')
    token = authorization.split(' ')[1]
    user = auth_manager.verify_token(token)
    if not user:
        raise HTTPException(status_code=401, detail='Invalid token')
    return user

@router.post("/register")
async def register(request: RegisterRequest):
    result = auth_manager.register_user(request.email, request.password, request.full_name)
    if not result['success']:
        raise HTTPException(status_code=400, detail=result['error'])
    return result

@router.post("/login")
async def login(request: LoginRequest):
    result = auth_manager.login(request.email, request.password)
    if not result['success']:
        raise HTTPException(status_code=401, detail=result['error'])
    return result

@router.get("/me")
async def get_current_user_info(user: dict = Depends(get_current_user)):
    return user

@router.post("/subscribe")
async def create_subscription(request: SubscriptionRequest, user: dict = Depends(get_current_user)):
    result = payment_processor.create_stripe_subscription(user['user_id'], request.plan_type, request.payment_method_id)
    if not result['success']:
        raise HTTPException(status_code=400, detail=result['error'])
    return result

@router.post("/pay-per-use")
async def pay_per_use(request: PayPerUseRequest, user: dict = Depends(get_current_user)):
    result = payment_processor.pay_per_use(user['user_id'], request.item_type, request.item_id, request.price)
    if not result['success']:
        raise HTTPException(status_code=400, detail=result['error'])
    return result

@router.get("/limits")
async def check_limits(user: dict = Depends(get_current_user)):
    gen_limits = auth_manager.check_limits(user['user_id'], 'generation')
    dl_limits = auth_manager.check_limits(user['user_id'], 'download')
    return {'generation': gen_limits, 'download': dl_limits}

@router.get("/subscription/plans")
async def get_subscription_plans():
    return {
        'plans': [
            {'tier': 'free', 'price': 0, 'period': 'monthly', 'generations': 10, 'downloads': 0, 'features': ['Standard quality', 'No downloads']},
            {'tier': 'monthly', 'price': 29.99, 'period': 'monthly', 'generations': 1000, 'downloads': 1000, 'features': ['Ultra quality', 'Unlimited downloads', 'Priority support']},
            {'tier': 'annual', 'price': 299.99, 'period': 'annual', 'generations': 20000, 'downloads': 20000, 'features': ['Ultra quality', 'Unlimited downloads', 'Priority support', '20% discount']},
            {'tier': 'pro', 'price': 0, 'period': 'lifetime', 'generations': -1, 'downloads': -1, 'features': ['Ultra quality', 'Unlimited everything', 'Admin access', 'Priority support']}
        ]
    }
