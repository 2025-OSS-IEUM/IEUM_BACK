# api/core/__init__.py

# ============================
# 1) core.py에서 가져오는 것들
# ============================
from .core import (
    client,
    db,
    users_collection,
    MONGO_URI,
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS,
    create_indexes,
)

# ============================
# 2) config.py에서 가져오는 것들
# ============================
from .config import settings   # ★ 추가된 부분

# ============================
# 3) security.py에서 가져오는 것들
# ============================
from .security import (
    verify_password,
    hash_password,
    create_access_token,
    create_refresh_token,
)
