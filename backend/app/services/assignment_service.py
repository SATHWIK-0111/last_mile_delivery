import math

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.agent import Agent
from app.models.order import Order
from app.services.tracking_service import add_event


def calculate_distance(
    latitude_1: float,
    longitude_1: float,
    latitude_2: float,
    longitude_2: float
) -> float:
    """
    Calculate the distance between two GPS coordinates
    using the Haversine formula.

    Returns distance in kilometers.
    """

    earth_radius_km = 6371.0

    lat1 = math.radians(latitude_1)
    lat2 = math.radians(latitude_2)

    delta_lat = math.radians(
        latitude_2 - latitude_1
    )

    delta_lon = math.radians(
        longitude_2 - longitude_1
    )

    a = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1)
        * math.cos(lat2)
        * math.sin(delta_lon / 2) ** 2
    )

    c = 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a)
    )

    return earth_radius_km * c


def assign_agent(
    *,
    order_id: int,
    agent_id: int,
    actor_id: int,
    actor_role: str,
    db: Session
) -> Order:
    """
    Manually assign an agent to an order.

    Validation:
    - Order must exist
    - Order must be CREATED
    - Agent must exist
    - Agent must be AVAILABLE
    - Agent must belong to the pickup zone

    On success:
    - order.agent_id = agent.id
    - order.current_status = ASSIGNED
    - agent becomes BUSY
    - tracking history is created
    """

    # -----------------------------------------
    # 1. Get order
    # -----------------------------------------

    order = db.get(Order, order_id)

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    # -----------------------------------------
    # 2. Validate order status
    # -----------------------------------------

    if order.current_status != "CREATED":
        raise HTTPException(
            status_code=400,
            detail="Only CREATED orders can be assigned"
        )

    # -----------------------------------------
    # 3. Get agent
    # -----------------------------------------

    agent = db.get(Agent, agent_id)

    if not agent:
        raise HTTPException(
            status_code=404,
            detail="Agent not found"
        )

    # -----------------------------------------
    # 4. Validate availability
    # -----------------------------------------

    if agent.availability_status != "AVAILABLE":
        raise HTTPException(
            status_code=400,
            detail="Agent is not currently available"
        )

    # -----------------------------------------
    # 5. Validate zone
    # -----------------------------------------

    if agent.zone_id != order.pickup_zone_id:
        raise HTTPException(
            status_code=400,
            detail=(
                "Agent is not assigned to the "
                "order pickup zone"
            )
        )

    # -----------------------------------------
    # 6. Assign agent
    # -----------------------------------------

    order.agent_id = agent.id
    order.current_status = "ASSIGNED"

    # Agent is now handling this order.
    agent.availability_status = "BUSY"

    # -----------------------------------------
    # 7. Create tracking history
    # -----------------------------------------

    add_event(
        order_id=order.id,
        status="ASSIGNED",
        actor_id=actor_id,
        actor_role=actor_role,
        remarks=f"Order manually assigned to agent {agent.id}",
        db=db
    )

    

    # -----------------------------------------
    # 8. Save
    # -----------------------------------------

    db.commit()
    db.refresh(order)

    return order


def auto_assign_agent(
    *,
    order_id: int,
    actor_id: int,
    actor_role: str,
    db: Session
) -> Order:
    """
    Automatically assign the nearest available agent
    in the order's pickup zone.

    Requirements:
    - Order must be CREATED
    - Pickup GPS coordinates must exist
    - Agent must be AVAILABLE
    - Agent must belong to pickup zone
    - Agent must have GPS coordinates

    On success:
    - nearest agent is assigned
    - order becomes ASSIGNED
    - agent becomes BUSY
    - tracking history is created
    """

    # -----------------------------------------
    # 1. Get order
    # -----------------------------------------

    order = db.get(Order, order_id)

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    # -----------------------------------------
    # 2. Validate order status
    # -----------------------------------------

    if order.current_status != "CREATED":
        raise HTTPException(
            status_code=400,
            detail="Only CREATED orders can be assigned"
        )

    # -----------------------------------------
    # 3. Validate pickup coordinates
    # -----------------------------------------

    if (
        order.pickup_latitude is None
        or order.pickup_longitude is None
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "Pickup latitude and longitude are "
                "required for automatic assignment"
            )
        )

    # -----------------------------------------
    # 4. Find available agents
    #    in the pickup zone
    # -----------------------------------------

    available_agents = (
        db.query(Agent)
        .filter(
            Agent.zone_id == order.pickup_zone_id,
            Agent.availability_status == "AVAILABLE",
            Agent.current_latitude.isnot(None),
            Agent.current_longitude.isnot(None)
        )
        .all()
    )

    if not available_agents:
        raise HTTPException(
            status_code=404,
            detail=(
                "No available agents with location "
                "found in the pickup zone"
            )
        )

    # -----------------------------------------
    # 5. Find nearest agent
    # -----------------------------------------

    nearest_agent = None
    nearest_distance = float("inf")

    for agent in available_agents:

        distance = calculate_distance(
            order.pickup_latitude,
            order.pickup_longitude,
            agent.current_latitude,
            agent.current_longitude
        )

        if distance < nearest_distance:
            nearest_distance = distance
            nearest_agent = agent

    # -----------------------------------------
    # 6. Safety check
    # -----------------------------------------

    if nearest_agent is None:
        raise HTTPException(
            status_code=500,
            detail="Unable to determine nearest agent"
        )

    # -----------------------------------------
    # 7. Assign agent
    # -----------------------------------------

    order.agent_id = nearest_agent.id
    order.current_status = "ASSIGNED"

    nearest_agent.availability_status = "BUSY"

    # -----------------------------------------
    # 8. Tracking history
    # -----------------------------------------

    add_event(
        order_id=order.id,
        status="ASSIGNED",
        actor_id=actor_id,
        actor_role=actor_role,
        remarks=(
            f"Automatically assigned to agent "
            f"{nearest_agent.id} "
            f"({nearest_distance:.2f} km away)"
        ),
        db=db
    )

    

    # -----------------------------------------
    # 9. Save
    # -----------------------------------------

    db.commit()
    db.refresh(order)

    return order

def reassign_order(
    *,
    order_id: int,
    actor_id: int,
    actor_role: str,
    db: Session
) -> Order:
    """
    Automatically assign a RESCHEDULED order to the
    nearest available agent in the pickup zone.
    """

    # -----------------------------------------
    # 1. Get order
    # -----------------------------------------

    order = db.get(Order, order_id)

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    # -----------------------------------------
    # 2. Validate order status
    # -----------------------------------------

    if order.current_status != "RESCHEDULED":
        raise HTTPException(
            status_code=400,
            detail="Only RESCHEDULED orders can be reassigned"
        )

    # -----------------------------------------
    # 3. Validate pickup coordinates
    # -----------------------------------------

    if (
        order.pickup_latitude is None
        or order.pickup_longitude is None
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "Pickup latitude and longitude are "
                "required for automatic reassignment"
            )
        )

    # -----------------------------------------
    # 4. Find available agents
    # -----------------------------------------

    available_agents = (
        db.query(Agent)
        .filter(
            Agent.zone_id == order.pickup_zone_id,
            Agent.availability_status == "AVAILABLE",
            Agent.current_latitude.isnot(None),
            Agent.current_longitude.isnot(None)
        )
        .all()
    )

    if not available_agents:
        raise HTTPException(
            status_code=404,
            detail=(
                "No available agents with location "
                "found in the pickup zone"
            )
        )

    # -----------------------------------------
    # 5. Find nearest agent
    # -----------------------------------------

    nearest_agent = None
    nearest_distance = float("inf")

    for agent in available_agents:

        distance = calculate_distance(
            order.pickup_latitude,
            order.pickup_longitude,
            agent.current_latitude,
            agent.current_longitude
        )

        if distance < nearest_distance:
            nearest_distance = distance
            nearest_agent = agent

    if nearest_agent is None:
        raise HTTPException(
            status_code=500,
            detail="Unable to determine nearest agent"
        )

    # -----------------------------------------
    # 6. Assign agent
    # -----------------------------------------

    order.agent_id = nearest_agent.id
    order.current_status = "ASSIGNED"

    nearest_agent.availability_status = "BUSY"

    # -----------------------------------------
    # 7. Tracking event
    # -----------------------------------------

    add_event(
        order_id=order.id,
        status="ASSIGNED",
        actor_id=actor_id,
        actor_role=actor_role,
        remarks=(
            f"Rescheduled order automatically reassigned "
            f"to agent {nearest_agent.id} "
            f"({nearest_distance:.2f} km away)"
        ),
        db=db
    )

    # -----------------------------------------
    # 8. Save
    # -----------------------------------------

    db.commit()
    db.refresh(order)

    return order