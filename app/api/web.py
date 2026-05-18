from fastapi import APIRouter, Request, Depends, Form, status, Response, File, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.exceptions import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.database import db_session
from app.auth import get_current_user_from_cookie, authenticate_user, create_access_token, get_password_hash
from app.crud.user import create_user, get_user_by_username
from app.crud.coupon import get_all_coupons, get_coupons_by_category
from app.services.coupon_service import create_coupon_from_text, pick_best_deal, pick_best_deal_by_category, process_uploaded_image, _estimate_savings
from app.schemas import UserCreate
from app.models import User, DiscountType

router = APIRouter(tags=["Web"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def home(request: Request, user: Optional[User] = Depends(get_current_user_from_cookie)):
    if user:
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login", response_class=HTMLResponse)
async def login(
    request: Request,
    response: Response,
    username: str = Form(...),
    password: str = Form(...),
    session: AsyncSession = Depends(db_session)
):
    user = await authenticate_user(username, password, session)
    if not user:
        # Simplistic error handling for flash messages placeholder
        return templates.TemplateResponse("login.html", {
            "request": request,
            "messages": [{"category": "danger", "text": "Invalid username or password"}]
        })
    
    access_token = create_access_token(subject=str(user.id))
    resp = RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    resp.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    return resp

@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/register", response_class=HTMLResponse)
async def register(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    session: AsyncSession = Depends(db_session)
):
    existing_user = await get_user_by_username(username, session)
    if existing_user:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "messages": [{"category": "danger", "text": "Username already taken"}]
        })
    
    user_model = User(
        username=username,
        hashed_password=get_password_hash(password)
    )
    user = await create_user(user_model, session)
    
    access_token = create_access_token(subject=str(user.id))
    resp = RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    resp.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    return resp

@router.get("/logout")
async def logout():
    resp = RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    resp.delete_cookie("access_token")
    return resp

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    category: Optional[str] = None,
    user: User = Depends(get_current_user_from_cookie),
    session: AsyncSession = Depends(db_session)
):
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    
    request.state.user = user

    if category and category != 'All':
        coupons = await get_coupons_by_category(category=category, user_id=user.id, session=session)
    else:
        coupons = await get_all_coupons(user_id=user.id, session=session)
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request, 
        "coupons": coupons,
        "current_category": category
    })

@router.get("/profile", response_class=HTMLResponse)
async def profile(
    request: Request,
    user: User = Depends(get_current_user_from_cookie),
    session: AsyncSession = Depends(db_session)
):
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    
    request.state.user = user
    coupons = await get_all_coupons(user_id=user.id, session=session)
    
    total_saved = 0.0
    percentage_count = 0
    
    for c in coupons:
        if c.discount_type == DiscountType.AMOUNT.value:
            total_saved += float(c.value)
        elif c.discount_type == DiscountType.PERCENTAGE.value:
            percentage_count += 1
            
    return templates.TemplateResponse("profile.html", {
        "request": request,
        "total_saved": total_saved,
        "percentage_count": percentage_count
    })

@router.get("/add-coupon", response_class=HTMLResponse)
async def add_coupon_page(
    request: Request,
    user: User = Depends(get_current_user_from_cookie)
):
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    request.state.user = user
    return templates.TemplateResponse("add_coupon.html", {"request": request})

@router.post("/submit-coupon", response_class=HTMLResponse)
async def add_coupon_submit(
    request: Request,
    user_text: str = Form(...),
    user: User = Depends(get_current_user_from_cookie),
    session: AsyncSession = Depends(db_session)
):
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    
    request.state.user = user
    try:
        await create_coupon_from_text(user_text, user.id, session)
        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "coupons": await get_all_coupons(user_id=user.id, session=session),
            "messages": [{"category": "success", "text": "Coupon added successfully!"}]
        })
    except Exception as e:
        return templates.TemplateResponse("add_coupon.html", {
            "request": request,
            "messages": [{"category": "danger", "text": f"Failed to parse coupon: {str(e)}"}]
        })
@router.get("/best-deal", response_class=HTMLResponse)
async def best_deal_get(
    request: Request,
    user: User = Depends(get_current_user_from_cookie)
):
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    request.state.user = user
    return templates.TemplateResponse("best_deal.html", {"request": request})

@router.post("/best-deal", response_class=HTMLResponse)
async def best_deal_post(
    request: Request,
    search_type: str = Form(...),
    search_value: str = Form(...),
    amount: float = Form(...),
    user: User = Depends(get_current_user_from_cookie),
    session: AsyncSession = Depends(db_session)
):
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    
    request.state.user = user
    if search_type == "platform":
        best_coupon = await pick_best_deal(search_value, amount, user.id, session)
        platform_searched = search_value
        category_searched = None
    else:
        best_coupon = await pick_best_deal_by_category(search_value, amount, user.id, session)
        category_searched = search_value
        platform_searched = None
    
    estimated_savings = _estimate_savings(best_coupon, amount) if best_coupon else 0.0

    return templates.TemplateResponse("best_deal.html", {
        "request": request,
        "search_type": search_type,
        "search_value": search_value,
        "platform_searched": platform_searched,
        "category_searched": category_searched,
        "amount_searched": amount,
        "best_coupon": best_coupon,
        "estimated_savings": estimated_savings,
        "searched": True
    })

@router.post("/add-coupon/image", response_class=HTMLResponse)
async def add_coupon_image(
    request: Request,
    file: UploadFile = File(...),
    user: User = Depends(get_current_user_from_cookie),
    session: AsyncSession = Depends(db_session)
):
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    
    request.state.user = user
    try:
        await process_uploaded_image(file, session, user.id)
        
        # PRG Pattern: return to dashboard with success message
        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "coupons": await get_all_coupons(user_id=user.id, session=session),
            "messages": [{"category": "success", "text": "Coupon extracted from image successfully!"}]
        })
    except HTTPException as e:
        return templates.TemplateResponse("add_coupon.html", {
            "request": request,
            "messages": [{"category": "danger", "text": e.detail}]
        })
    except Exception as e:
        return templates.TemplateResponse("add_coupon.html", {
            "request": request,
            "messages": [{"category": "danger", "text": f"Failed to upload image: {str(e)}"}]
        })
