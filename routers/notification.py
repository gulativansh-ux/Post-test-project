from fastapi import APIRouter, Depends, HTTPException, WebSocket
from fastapi import WebSocketDisconnect
from database.connection import SessionDep
from database.model import Notification
from security.jwtUtil import get_current_user, authenticate_websocket_user
from security.websocket import notification_manager
from sqlmodel import select, func

notifications_router = APIRouter(tags=["Notifications"])


@notifications_router.get("")
def get_notifications(
    session: SessionDep,
    user_detail=Depends(get_current_user),
):
    statement = (
        select(Notification)
        .where(
            Notification.user_id == user_detail.id,
            Notification.is_read == False,
        )
    )

    return session.exec(statement).all()


@notifications_router.get("/unread-count")
def get_unread_count(
    session: SessionDep,
    user_detail=Depends(get_current_user),
):
    count = session.exec(
        select(func.count(Notification.id)).where(
            Notification.user_id == user_detail.id,
            Notification.is_read == False,
        )
    ).one()

    return {"count": count}


@notifications_router.patch("/{notification_id}/read")
def mark_notification_read(
    notification_id: int,
    session: SessionDep,
    user_detail=Depends(get_current_user),
):
    notification = session.exec(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == user_detail.id,
        )
    ).first()

    if not notification:
        raise HTTPException(
            status_code=404,
            detail="Notification not found",
        )

    if not notification.is_read:
        notification.is_read = True
        session.add(notification)
        session.commit()
        session.refresh(notification)

    return {
        "message": "Notification marked as read",
        "id": notification.id,
        "is_read": notification.is_read,
    }


@notifications_router.websocket("/ws")
async def notification_websocket(
    websocket: WebSocket,
    session: SessionDep,
):
    user_id = await authenticate_websocket_user(websocket, session)

    if user_id is None:
        await websocket.close(code=1008)
        return

    await notification_manager.connect(user_id, websocket)

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        notification_manager.disconnect(user_id, websocket)
