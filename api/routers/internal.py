from fastapi import APIRouter, HTTPException, status

router = APIRouter(
    prefix="/internal",
    tags=["Internal"]
)

@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    try:
        db_status = "ok"
        external_api = "ok"

        if db_status != "ok" or external_api != "ok":
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="내부 서비스 일부에 연결할 수 없습니다."
            )

        return {
            "status": "ok",
            "details": {
                "db": db_status,
                "external_api": external_api
            }
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"내부 서버 오류 발생: {e}"
        )

@router.get("/metrics", status_code=status.HTTP_200_OK)
async def get_metrics():
    try:
        uptime_seconds = 3600
        requests_total = 128
        return {"uptime_seconds": uptime_seconds, "requests_total": requests_total}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"내부 메트릭 수집 오류: {e}"
        )
