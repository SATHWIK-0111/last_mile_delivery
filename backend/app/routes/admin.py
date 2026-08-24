from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.services.assignment_service import (
    assign_agent,
    auto_assign_agent
)
from app.database import get_db
from app.models.agent import Agent
from app.models.cod_charge import CodCharge
from app.models.rate_card import RateCard
from app.models.user import User
from app.models.zone import Zone
from app.models.zone_area import ZoneArea
from app.schemas.admin import (
    AgentCreate,
    AgentResponse,
    AgentZoneUpdate,
    AreaCreate,
    AreaResponse,
    AreaUpdate,
    CodChargeCreate,
    CodChargeResponse,
    CodChargeUpdate,
    RateCardCreate,
    RateCardResponse,
    RateCardUpdate,
    ZoneCreate,
    ZoneResponse,
    ZoneUpdate,
)
from app.utils.auth import hash_password
from app.utils.permissions import require_admin
from app.schemas.order import (
    OrderCalculateRequest,
    OrderCalculateResponse,
)
from app.services.rate_engine import calculate_rate
from app.schemas.order import (
    OrderCalculateRequest,
    OrderCalculateResponse,
    OrderCreateRequest,
    OrderResponse,
)
from app.services.order_service import create_order
from app.models.order import Order
router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)
from app.services.assignment_service import (
    assign_agent,
    auto_assign_agent
)
from app.services.tracking_service import get_order_tracking
from app.schemas.order import OrderTrackingResponse

@router.post(
    "/zones",
    response_model=ZoneResponse,
    status_code=status.HTTP_201_CREATED
)
def create_zone(
    request: ZoneCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):

    existing = (
        db.query(Zone)
        .filter(Zone.name == request.name)
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Zone already exists"
        )

    zone = Zone(
        name=request.name
    )

    db.add(zone)
    db.commit()
    db.refresh(zone)

    return zone


@router.get(
    "/zones",
    response_model=list[ZoneResponse]
)
def get_zones(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):

    return db.query(Zone).all()


@router.get(
    "/zones/{zone_id}",
    response_model=ZoneResponse
)
def get_zone(
    zone_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):

    zone = db.get(Zone, zone_id)

    if not zone:
        raise HTTPException(
            status_code=404,
            detail="Zone not found"
        )

    return zone


@router.put(
    "/zones/{zone_id}",
    response_model=ZoneResponse
)
def update_zone(
    zone_id: int,
    request: ZoneUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):

    zone = db.get(Zone, zone_id)

    if not zone:
        raise HTTPException(
            status_code=404,
            detail="Zone not found"
        )

    zone.name = request.name

    db.commit()
    db.refresh(zone)

    return zone


@router.delete(
    "/zones/{zone_id}"
)
def delete_zone(
    zone_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):

    zone = db.get(Zone, zone_id)

    if not zone:
        raise HTTPException(
            status_code=404,
            detail="Zone not found"
        )

    db.delete(zone)
    db.commit()

    return {
        "message": "Zone deleted successfully"
    }
    
# ==========================================
# AREAS
# ==========================================

@router.post(
    "/zones/{zone_id}/areas",
    response_model=AreaResponse,
    status_code=status.HTTP_201_CREATED
)
def create_area(
    zone_id: int,
    request: AreaCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):

    zone = db.get(Zone, zone_id)

    if not zone:
        raise HTTPException(
            status_code=404,
            detail="Zone not found"
        )

    area = ZoneArea(
        zone_id=zone_id,
        area_name=request.area_name
    )

    db.add(area)
    db.commit()
    db.refresh(area)

    return area


@router.get(
    "/zones/{zone_id}/areas",
    response_model=list[AreaResponse]
)
def get_zone_areas(
    zone_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):

    zone = db.get(Zone, zone_id)

    if not zone:
        raise HTTPException(
            status_code=404,
            detail="Zone not found"
        )

    return (
        db.query(ZoneArea)
        .filter(ZoneArea.zone_id == zone_id)
        .all()
    )


@router.put(
    "/areas/{area_id}",
    response_model=AreaResponse
)
def update_area(
    area_id: int,
    request: AreaUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):

    area = db.get(ZoneArea, area_id)

    if not area:
        raise HTTPException(
            status_code=404,
            detail="Area not found"
        )

    area.area_name = request.area_name

    db.commit()
    db.refresh(area)

    return area


@router.delete(
    "/areas/{area_id}"
)
def delete_area(
    area_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):

    area = db.get(ZoneArea, area_id)

    if not area:
        raise HTTPException(
            status_code=404,
            detail="Area not found"
        )

    db.delete(area)
    db.commit()

    return {
        "message": "Area deleted successfully"
    }
    
# ==========================================
# RATE CARDS
# ==========================================

@router.post(
    "/rates",
    response_model=RateCardResponse,
    status_code=status.HTTP_201_CREATED
)
def create_rate_card(
    request: RateCardCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):

    order_type = request.order_type.upper()
    zone_type = request.zone_type.upper()

    if order_type not in {"B2B", "B2C"}:
        raise HTTPException(
            status_code=400,
            detail="order_type must be B2B or B2C"
        )

    if zone_type not in {"INTRA", "INTER"}:
        raise HTTPException(
            status_code=400,
            detail="zone_type must be INTRA or INTER"
        )

    existing = (
        db.query(RateCard)
        .filter(
            RateCard.order_type == order_type,
            RateCard.zone_type == zone_type
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Rate card already exists for this combination"
        )

    rate = RateCard(
        order_type=order_type,
        zone_type=zone_type,
        base_rate=request.base_rate,
        additional_rate=request.additional_rate,
        weight_limit=request.weight_limit
    )

    db.add(rate)
    db.commit()
    db.refresh(rate)

    return rate


@router.get(
    "/rates",
    response_model=list[RateCardResponse]
)
def get_rate_cards(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):

    return db.query(RateCard).all()


@router.put(
    "/rates/{rate_id}",
    response_model=RateCardResponse
)
def update_rate_card(
    rate_id: int,
    request: RateCardUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):

    rate = db.get(RateCard, rate_id)

    if not rate:
        raise HTTPException(
            status_code=404,
            detail="Rate card not found"
        )

    rate.base_rate = request.base_rate
    rate.additional_rate = request.additional_rate
    rate.weight_limit = request.weight_limit

    db.commit()
    db.refresh(rate)

    return rate

# ==========================================
# COD CHARGES
# ==========================================

@router.post(
    "/cod-charges",
    response_model=CodChargeResponse,
    status_code=status.HTTP_201_CREATED
)
def create_cod_charge(
    request: CodChargeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):

    order_type = request.order_type.upper()

    if order_type not in {"B2B", "B2C"}:
        raise HTTPException(
            status_code=400,
            detail="order_type must be B2B or B2C"
        )

    existing = (
        db.query(CodCharge)
        .filter(CodCharge.order_type == order_type)
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="COD charge already exists for this order type"
        )

    cod = CodCharge(
        order_type=order_type,
        charge=request.charge
    )

    db.add(cod)
    db.commit()
    db.refresh(cod)

    return cod


@router.get(
    "/cod-charges",
    response_model=list[CodChargeResponse]
)
def get_cod_charges(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):

    return db.query(CodCharge).all()


@router.put(
    "/cod-charges/{cod_id}",
    response_model=CodChargeResponse
)
def update_cod_charge(
    cod_id: int,
    request: CodChargeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):

    cod = db.get(CodCharge, cod_id)

    if not cod:
        raise HTTPException(
            status_code=404,
            detail="COD charge not found"
        )

    cod.charge = request.charge

    db.commit()
    db.refresh(cod)

    return cod

# ==========================================
# AGENTS
# ==========================================

@router.get(
    "/agents",
    response_model=list[AgentResponse]
)
def get_agents(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):

    return db.query(Agent).all()


@router.post(
    "/agents",
    response_model=AgentResponse,
    status_code=status.HTTP_201_CREATED
)
def create_agent(
    request: AgentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):

    existing_user = (
        db.query(User)
        .filter(User.email == request.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    if request.zone_id is not None:
        zone = db.get(Zone, request.zone_id)

        if not zone:
            raise HTTPException(
                status_code=404,
                detail="Zone not found"
            )

    user = User(
        name=request.name,
        email=request.email,
        phone=request.phone,
        password_hash=hash_password(request.password),
        role="AGENT"
    )

    db.add(user)
    db.flush()

    agent = Agent(
        user_id=user.id,
        zone_id=request.zone_id,
        availability_status="OFFLINE"
    )

    db.add(agent)
    db.commit()
    db.refresh(agent)

    return agent


@router.put(
    "/agents/{agent_id}/zone",
    response_model=AgentResponse
)
def update_agent_zone(
    agent_id: int,
    request: AgentZoneUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):

    agent = db.get(Agent, agent_id)

    if not agent:
        raise HTTPException(
            status_code=404,
            detail="Agent not found"
        )

    zone = db.get(Zone, request.zone_id)

    if not zone:
        raise HTTPException(
            status_code=404,
            detail="Zone not found"
        )

    agent.zone_id = request.zone_id

    db.commit()
    db.refresh(agent)

    return agent
@router.get(
    "/orders/{order_id}/tracking",
    response_model=OrderTrackingResponse
)
def get_admin_order_tracking(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    return get_order_tracking(
        order_id=order_id,
        db=db
    )
    

@router.post(
    "/orders/calculate",
    response_model=OrderCalculateResponse
)
def calculate_admin_order_charge(
    request: OrderCalculateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):

    return calculate_rate(
        pickup_address=request.pickup_address,
        drop_address=request.drop_address,
        length=request.length,
        breadth=request.breadth,
        height=request.height,
        actual_weight=request.actual_weight,
        order_type=request.order_type,
        payment_type=request.payment_type,
        db=db
    )
@router.post(
    "/orders/{order_id}/auto-assign",
    response_model=OrderResponse
)
def automatically_assign_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    return auto_assign_agent(
        order_id=order_id,
        actor_id=current_user.id,
        actor_role="ADMIN",
        db=db
    )
@router.post(
    "/orders",
    response_model=OrderResponse,
    status_code=201
)
def create_admin_order(
    customer_id: int,
    request: OrderCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):

    return create_order(
        customer_id=customer_id,

        actor_id=current_user.id,
        actor_role="ADMIN",

        pickup_address=request.pickup_address,
        drop_address=request.drop_address,
        pickup_latitude=request.pickup_latitude,
        pickup_longitude=request.pickup_longitude,
        length=request.length,
        breadth=request.breadth,
        height=request.height,

        actual_weight=request.actual_weight,

        order_type=request.order_type,
        payment_type=request.payment_type,

        db=db
    )
@router.post(
    "/orders/{order_id}/assign",
    response_model=OrderResponse
)
def assign_order_agent(
    order_id: int,
    agent_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    return assign_agent(
        order_id=order_id,
        agent_id=agent_id,
        actor_id=current_user.id,
        actor_role="ADMIN",
        db=db
    )
@router.get(
    "/orders",
    response_model=list[OrderResponse]
)
def get_all_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):

    return (
        db.query(Order)
        .order_by(
            Order.created_at.desc()
        )
        .all()
    )

@router.get(
    "/orders/{order_id}",
    response_model=OrderResponse
)
def get_admin_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):

    order = db.get(
        Order,
        order_id
    )

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    return order