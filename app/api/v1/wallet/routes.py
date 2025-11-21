from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from datetime import datetime, date

from app.db.session import get_db
from app.core.jwt import get_current_user
from app.core.security import verify_pin

from app.models.user import User
from app.models.wallet import Wallet
from app.models.transaction import Transaction, TransactionType, TransactionStatus

from app.schemas.wallet import WalletRead, AddMoneyRequest, TransferRequest
from app.schemas.transaction import TransactionRead
from app.schemas.paginated import PaginatedTransactions

router = APIRouter(
    prefix="/wallet",
    tags=["Wallet"]
)

@router.get("/me", response_model=WalletRead)
async def get_my_wallet(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    wallet = (
        await db.execute(select(Wallet).where(Wallet.user_id == current_user.id))
    ).scalar_one_or_none()

    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")

    return wallet
# =====================================================
# ADD MONEY
# =====================================================
@router.post("/add-money", response_model=WalletRead)
async def add_money(
    data: AddMoneyRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        print(f"🔄 Add money request received for user: {current_user.id}")
        print(f"📦 Request data: amount={data.amount}, pin_length={len(data.pin)}")

        if data.amount <= 0:
            raise HTTPException(400, "Amount must be positive")

        # Get user with pin_hashed
        print(f"🔍 Fetching user with ID: {current_user.id}")
        user_result = await db.execute(select(User).where(User.id == current_user.id))
        user = user_result.scalar_one_or_none()

        if not user:
            print("❌ User not found")
            raise HTTPException(404, "User not found")

        print(f"✅ User found: {user.email}")
        print(f"🔐 User has PIN hashed: {bool(user.pin_hashed)}")

        # Verify PIN
        print(f"🔑 Verifying PIN...")
        pin_verified = verify_pin(data.pin, user.pin_hashed)
        print(f"🔑 PIN verification result: {pin_verified}")
        
        # ✅ FIX: Change from 401 to 400 for PIN errors
        if not pin_verified:
            raise HTTPException(400, "Invalid PIN")  # Changed from 401 to 400

        # Get wallet
        print(f"💰 Fetching wallet for user: {current_user.id}")
        wallet_result = await db.execute(select(Wallet).where(Wallet.user_id == current_user.id))
        wallet = wallet_result.scalar_one_or_none()

        if not wallet:
            print("❌ Wallet not found")
            raise HTTPException(404, "Wallet not found")

        print(f"✅ Wallet found. Current balance: {wallet.balance}, Type: {type(wallet.balance)}")
        print(f"💵 Adding amount: {data.amount}, Type: {type(data.amount)}")

        # Convert float to Decimal before addition
        from decimal import Decimal
        amount_decimal = Decimal(str(data.amount))
        print(f"💵 Converted amount: {amount_decimal}, Type: {type(amount_decimal)}")

        # Add money (now both are Decimal)
        old_balance = wallet.balance
        wallet.balance += amount_decimal
        print(f"📈 Balance updated: {old_balance} -> {wallet.balance}")

        # Create transaction record
        print("📝 Creating transaction record...")
        tx = Transaction(
            wallet_id=wallet.id,
            amount=amount_decimal,
            type=TransactionType.ADD_MONEY,
            status=TransactionStatus.SUCCESS,
            counterparty="SYSTEM",
        )

        db.add(tx)
        print("💾 Committing to database...")
        await db.commit()
        await db.refresh(wallet)
        print(f"✅ Money added successfully. Final balance: {wallet.balance}")

        return wallet

    except HTTPException as he:
        print(f"🚨 HTTPException: {he.status_code} - {he.detail}")
        raise he
    except Exception as e:
        print(f"💥 UNEXPECTED ERROR in add_money:")
        print(f"   Error type: {type(e).__name__}")
        print(f"   Error message: {str(e)}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")
        raise HTTPException(500, f"Internal server error: {str(e)}")

@router.post("/transfer", response_model=WalletRead)
async def transfer_money(
    data: TransferRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        print(f"🔄 Transfer request: {current_user.email} -> {data.to_email}, Amount: {data.amount}")

        if data.amount <= 0:
            raise HTTPException(400, "Amount must be positive")

        # Convert amount to Decimal
        from decimal import Decimal
        amount_decimal = Decimal(str(data.amount))

        # Get user with pin_hashed
        user_result = await db.execute(select(User).where(User.id == current_user.id))
        user = user_result.scalar_one_or_none()

        if not user:
            raise HTTPException(404, "User not found")

        # Verify PIN
        # ✅ FIX: Change from 401 to 400 for PIN errors
        if not verify_pin(data.pin, user.pin_hashed):
            raise HTTPException(400, "Invalid PIN")  # Changed from 401 to 400

        # Sender wallet
        sender_wallet = (
            await db.execute(select(Wallet).where(Wallet.user_id == current_user.id))
        ).scalar_one_or_none()

        if not sender_wallet:
            raise HTTPException(404, "Sender wallet not found")

        # Receiver user
        receiver_user = (
            await db.execute(select(User).where(User.email == data.to_email))
        ).scalar_one_or_none()

        if not receiver_user:
            raise HTTPException(404, "Receiver not found")

        receiver_wallet = (
            await db.execute(select(Wallet).where(Wallet.user_id == receiver_user.id))
        ).scalar_one_or_none()

        if not receiver_wallet:
            raise HTTPException(404, "Receiver wallet not found")

        # Not enough balance (using Decimal for comparison)
        if sender_wallet.balance < amount_decimal:
            tx = Transaction(
                wallet_id=sender_wallet.id,
                amount=amount_decimal,
                type=TransactionType.TRANSFER,
                status=TransactionStatus.FAILED,
                counterparty=receiver_user.email
            )
            db.add(tx)
            await db.commit()
            raise HTTPException(400, "Insufficient balance")

        # Transfer (using Decimal)
        sender_wallet.balance -= amount_decimal
        receiver_wallet.balance += amount_decimal

        tx_sender = Transaction(
            wallet_id=sender_wallet.id,
            amount=amount_decimal,
            type=TransactionType.TRANSFER,
            status=TransactionStatus.SUCCESS,
            counterparty=receiver_user.email
        )

        tx_receiver = Transaction(
            wallet_id=receiver_wallet.id,
            amount=amount_decimal,
            type=TransactionType.RECEIVE,
            status=TransactionStatus.SUCCESS,
            counterparty=current_user.email
        )

        db.add(tx_sender)
        db.add(tx_receiver)
        await db.commit()
        await db.refresh(sender_wallet)

        print(f"✅ Transfer successful. New balance: {sender_wallet.balance}")
        return sender_wallet

    except Exception as e:
        print(f"❌ Transfer error: {e}")
        raise HTTPException(500, f"Transfer failed: {str(e)}")
# =====================================================
# TRANSACTION HISTORY
# =====================================================
@router.get("/history", response_model=PaginatedTransactions)
async def get_transaction_history(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    status: Optional[TransactionStatus] = Query(None),
    type: Optional[TransactionType] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Get current wallet
    wallet = (
        await db.execute(select(Wallet).where(Wallet.user_id == current_user.id))
    ).scalar_one_or_none()

    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")

    # Base query
    query = select(Transaction).where(Transaction.wallet_id == wallet.id)

    # Apply filters
    if status:
        query = query.where(Transaction.status == status)
    if type:
        query = query.where(Transaction.type == type)

    # Handle date filters
    if start_date:
        start_datetime = datetime.combine(start_date, datetime.min.time())
        query = query.where(Transaction.created_at >= start_datetime)

    if end_date:
        end_datetime = datetime.combine(end_date, datetime.max.time())
        query = query.where(Transaction.created_at <= end_datetime)

    # Count filtered records
    count_query = select(func.count()).select_from(query.subquery())
    total_items = (await db.execute(count_query)).scalar_one()

    # Pagination
    offset = (page - 1) * limit
    total_pages = (total_items + limit - 1) // limit if total_items else 0
    next_page = page + 1 if page * limit < total_items else None
    prev_page = page - 1 if page > 1 else None

    # Fetch paginated results
    tx_result = await db.execute(
        query.order_by(Transaction.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    transactions = tx_result.scalars().all()

    # Map to schema
    data = [
        TransactionRead(
            id=tx.id,
            wallet_id=tx.wallet_id,
            amount=tx.amount,
            type=tx.type,
            status=tx.status,
            provider_tx_id=tx.provider_tx_id,
            counterparty=tx.counterparty,
        )
        for tx in transactions
    ]

    # Response
    return PaginatedTransactions(
        page=page,
        limit=limit,
        total=total_items,
        total_pages=total_pages,
        next_page=next_page,
        prev_page=prev_page,
        data=data,
    )