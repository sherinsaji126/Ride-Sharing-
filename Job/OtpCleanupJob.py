from Database import SessionLocal
from Models import PasswordResetOTP
from datetime import datetime
from Services.EmailService import send_email
from dotenv import load_dotenv
import os

load_dotenv("Credentials.env")


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
        send_email(os.getenv("SENDER_EMAIL"),subject="OTP Cleanup Job Failed",body=body)

    finally:
        db.close()

if __name__ == "__main__":
    cleanup_otp_record()


    



# 2. query to fetch the records and count the records 
# 3. log it to the file 
# 4. the delete it 
# 5. close db conneciton
# 6. the send this log thorugh mail for success and failure.