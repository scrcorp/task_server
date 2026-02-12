from supabase import create_client, Client
from app.core.config import settings

def get_supabase() -> Client:
    if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
        print("⚠️ Warning: SUPABASE_URL or SUPABASE_KEY is not set.")
        # 빈 클라이언트를 반환하거나 에러를 낼 수 있지만, 여기서는 초기화만 시도합니다.
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

supabase: Client = get_supabase()
