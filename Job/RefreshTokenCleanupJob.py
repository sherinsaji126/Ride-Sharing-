from Database import SessionLocal
from Models import RefreshToken
from datetime import datetime
from Services.EmailService import send_email
from dotenv import load_dotenv
import os
import logging
from logging.handlers import TimedRotatingFileHandler

load_dotenv("Credentials.env")

log_dir=r"C:\\Users\shsaji\\OneDrive - Capgemini\\CG docs\\Logs\\Refresh Token Logs"

if not os.path.exists(log_dir):
    os.makedirs(log_dir)
handler = TimedRotatingFileHandler(
filename=os.path.join(log_dir, "Refresh_Token_cleanup.log"),
when="midnight",
interval=1,
backupCount=30
)
formatter = logging.Formatter(
"%(asctime)s | %(levelname)s | %(message)s"
)
handler.setFormatter(formatter)
logger = logging.getLogger("REFRESH_TOKEN_CLEANUP")
logger.setLevel(logging.INFO)
logger.addHandler(handler)


def cleanup_refresh_tokens():

    try:

        start_time = datetime.now()

        db = SessionLocal()

        expired_token_count = db.query(RefreshToken).filter(RefreshToken.expires_at <= datetime.now()).count()

        revoked_token_count = db.query(RefreshToken).filter(RefreshToken.is_revoked == True).count()

        total_deleted = expired_token_count + revoked_token_count

        db.query(RefreshToken).filter(RefreshToken.expires_at <= datetime.now()).delete(synchronize_session=False)

        db.query(RefreshToken).filter( RefreshToken.is_revoked == True).delete(synchronize_session=False)

        db.commit()

        end_time = datetime.now()

        body = f"""
REFRESH TOKEN CLEANUP JOB SUCCESS

Start Time : {start_time}
End Time   : {end_time}

Expired Tokens Deleted : {expired_token_count}

Revoked Tokens Deleted : {revoked_token_count}

Total Records Deleted : {total_deleted}

Status : SUCCESS
"""

        send_email(os.getenv("SENDER_EMAIL"),subject="Refresh Token Cleanup Job Success",body=body)

    except Exception as e:

        db.rollback()

        body = f"""
REFRESH TOKEN CLEANUP JOB FAILED

Start Time : {start_time}

Error : {str(e)}

Status : FAILED
"""

        send_email(os.getenv("SENDER_EMAIL"),subject="Refresh Token Cleanup Job Failed",body=body)

    finally:

        db.close()


if __name__ == "__main__":
    cleanup_refresh_tokens()