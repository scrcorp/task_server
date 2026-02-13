from supabase import create_client, Client
from app.core.config import settings

def get_supabase() -> Client:
    if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
        print("⚠️ Warning: SUPABASE_URL or SUPABASE_KEY is not set.")
        # Proceed with initialization even without credentials.
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

supabase: Client = get_supabase()
