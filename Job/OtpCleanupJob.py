from Database import SessionLocal
from Models import PasswordResetOTP
from datetime import datetime
from Services.EmailService import send_email
from dotenv import load_dotenv
import os
import logging
from logging.handlers import TimedRotatingFileHandler

load_dotenv("Credentials.env")

log_dir=r"C:\\Users\shsaji\\OneDrive - Capgemini\\CG docs\\Logs"

if not os.path.exists(log_dir):
    os.makedirs(log_dir)
#     logging.basicConfig(
#     filename="Logs/otp_cleanup.log",
#     level=logging.INFO,
#     format="%(asctime)s | %(levelname)s | %(message)s"
#     )
handler = TimedRotatingFileHandler(
filename=os.path.join(log_dir, "otp_cleanup.log"),
# filename="Logs/otp_cleanup.log",
when="midnight",
interval=1,
backupCount=30
)
formatter = logging.Formatter(
"%(asctime)s | %(levelname)s | %(message)s"
)
handler.setFormatter(formatter)
logger = logging.getLogger("OTP_CLEANUP")
logger.setLevel(logging.INFO)
logger.addHandler(handler)


# async def cleanup_otp_record(db:Annotated[Session,Depends(get_db)]): why i can't use this
def cleanup_otp_record():
    try:

        start_time=datetime.now()

        db=SessionLocal()

        #why used .all() below
        otp_records_to_delete=db.query(PasswordResetOTP).filter((PasswordResetOTP.is_verified==True) | (PasswordResetOTP.is_used==True)).all()
        record_count=len(otp_records_to_delete)
        db.query(PasswordResetOTP).filter((PasswordResetOTP.is_verified==True) | (PasswordResetOTP.is_used==True)).delete(synchronize_session=False)
        db.commit()

        end_time=datetime.now()

        body=f"""
        OTP CLEANUP JOB SUCCESS

        Start Time : {start_time}
        End Time : {end_time}

        Records Deleted : {record_count}

        Status : SUCCESS
        """
        logger.info(body)
        # why I can't just write body -> because a positional argument cannot comes after keyword arguments.
        send_email(os.getenv("SENDER_EMAIL"),subject="OTP Cleanup Job Success",body=body)

    except Exception as e:
        db.rollback() #why ?


        body= f"""
        OTP Cleanup Job Failed

        Start Time : {start_time}

        Error :{str(e)} # why converting in string ?

        Status : FAILED
        """
        logger.error(body)
        send_email(os.getenv("SENDER_EMAIL"),subject="OTP Cleanup Job Failed",body=body)

    finally:
        db.close()

if __name__ == "__main__":
    cleanup_otp_record()


