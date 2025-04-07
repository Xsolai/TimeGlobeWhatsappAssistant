from typing import List
from fastapi.responses import JSONResponse
from fastapi import APIRouter, Depends, HTTPException, status, Query
from ..services.dashboard_service import DashboardService
from ..schemas.auth import User
from ..core.dependencies import get_dashboard_service, get_current_user
from ..logger import main_logger

router = APIRouter()


@router.get("/overview")
def overview(
    current_user: User = Depends(get_current_user),
    service: DashboardService = Depends(get_dashboard_service),
):
    """Retrieves overview for the current user."""
    main_logger.info(f"Fetching overview for user {current_user.id}.")
    return service.overview(current_user.id)


@router.get("/appointments")
def get_appointment(
    range: str = Query("30d", regex="^(7d|30d|90d)$"),
    current_user: User = Depends(get_current_user),
    service: DashboardService = Depends(get_dashboard_service),
):
    """Retrieves appointments for the current user."""
    main_logger.info(f"Fetching appointments for user {current_user.id}.")
    return service.get_appointment(range, current_user.id)


@router.get("/top-services")
def get_top_service(
    current_user: User = Depends(get_current_user),
    service: DashboardService = Depends(get_dashboard_service),
):
    """Retrieves top services for the current user."""
    main_logger.info(f"Fetching top services for user {current_user.id}.")
    return service.get_top_services(current_user.id)


@router.get("/top-customer")
def get_top_customer(
    current_user: User = Depends(get_current_user),
    service: DashboardService = Depends(get_dashboard_service),
):
    """Retrieves top customer for the current user."""
    main_logger.info(f"Fetching top customer for user {current_user.id}.")
    return service.get_top_customers(current_user.id)


@router.get("/ai-logs")
def get_ai_logs(
    limit: int = Query(10, ge=1, le=50),
    service: DashboardService = Depends(get_dashboard_service),
):
    """Reterive most recent ai logs for audit/debug"""
    return service.get_ai_logs(limit=limit)


@router.get("/ai-performance")
def get_ai_performance(
    current_user: User = Depends(get_current_user),
    service: DashboardService = Depends(get_dashboard_service),
):
    """Reterive most recent ai logs for audit/debug"""
    return service.get_ai_perfomance(user_id=current_user.id)
