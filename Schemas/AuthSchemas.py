from pydantic import field_validator, EmailStr,BaseModel,model_validator
import re



# ************************************Login************************************************
# Request Model
class UserDetailsLogin(BaseModel):

     # dependency -> package email-validator
     # EmailStr is required to check if valid email address is entered that it. 
     # It does not automatically strip spaces and convert to lowercase for this we need to use field validator
    
    login:str
    password:str

    @field_validator("login", mode="before")
    @classmethod
    def validate_login(cls, value):
        value = value.strip()
        if not value:
            raise ValueError("Field cannot be empty")
        return value

    @field_validator("password")
    @classmethod
    def validate_password(cls, value):
        value = value.strip()
        if not value:
                raise ValueError("Password field cannot be empty")
        return value

# ************************************Register************************************************

# Request Model
class UserDetails(BaseModel):

     # dependency -> package email-validator
     # EmailStr is required to check if valid email address is entered that it. 
     # It does not automatically strip spaces and convert to lowercase for this we need to use field validator
    
    email_id:EmailStr
    password:str
    username:str

    @field_validator("email_id", mode="before")
    @classmethod
    def validate_email(cls, value):
        value = value.strip().lower()

        if len(value) > 255:
            raise ValueError("Email must not exceed 255 characters")

        return value


    @field_validator("username")
    @classmethod
    def validate_username(cls, value):
        if len(value) < 3 or len(value) > 30:
            raise ValueError("Username must be between 3 and 30 characters")
        if not re.match(r"^[a-zA-Z0-9._]+$", value):
            raise ValueError("Username can only contain letters, numbers, dots and underscores")
        return value


    @field_validator("password")
    @classmethod
    def validate_password(cls, value):
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must contain an uppercase letter")
        if not re.search(r"[a-z]", value):
            raise ValueError("Password must contain a lowercase letter")
        if not re.search(r"\d", value):
            raise ValueError("Password must contain a digit")
        return value


#Response Model
class RegisterUser(BaseModel):
    email_id: EmailStr
    username: str
    message: str

# ************************************Forgot Password********************************************

# Request Model
class ChangePassword(BaseModel):
    email_id:EmailStr

    @field_validator("email_id", mode="before")
    @classmethod
    def validate_email(cls, value):
        value = value.strip().lower()

        if len(value) > 255:
            raise ValueError("Email must not exceed 255 characters")

        return value

# *************************************OTP Verification******************************************

# Request Model
class VerificationOTP(BaseModel):
    email_id:EmailStr
    entered_otp:str

    @field_validator("email_id", mode="before")
    @classmethod
    def validate_email(cls, value):
        value = value.strip().lower()

        if len(value) > 255:
            raise ValueError("Email must not exceed 255 characters")

        return value

# ***************************************PasswordReset*******************************************

# Request Model
class PasswordReset(BaseModel):
    email_id:EmailStr
    new_password:str
    confirm_password:str

    @field_validator("email_id", mode="before")
    @classmethod
    def validate_email(cls, value):
        value = value.strip().lower()

        if len(value) > 255:
            raise ValueError("Email must not exceed 255 characters")

        return value
    
    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, value):
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must contain an uppercase letter")
        if not re.search(r"[a-z]", value):
            raise ValueError("Password must contain a lowercase letter")
        if not re.search(r"\d", value):
            raise ValueError("Password must contain a digit")
        return value

    # Since confirm_password must be compared with new_password, use a validator that has access to other fields
    # @field_validator("confirm_password")
    # @classmethod
    # def validate_confirm_password(cls, value, info: ValidationInfo):
    #         if value != info.data.get("new_password"):
    #           raise ValueError("Passwords do not match")
    #         return value
    
    # Instead of validating confirm_password separately, you let Pydantic create the entire object first, and then you compare both fields.
    @model_validator(mode="after")
    def validate_passwords(self):
        if self.new_password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self