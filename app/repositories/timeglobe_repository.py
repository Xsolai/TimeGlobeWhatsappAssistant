import logging
from sqlalchemy.orm import Session
from ..models.customer_model import CustomerModel
from ..models.booked_appointment import BookModel
from ..models.booking_detail import BookingDetail
from ..models.appointment_status import AppointmentStatus
from datetime import datetime
from ..logger import (
    main_logger,
)


class TimeGlobeRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_customer(self, mobile_number: str) -> CustomerModel:
        try:
            main_logger.info(f"Fetching customer with mobile number: {mobile_number}")

            if not mobile_number.startswith("+"):
                mobile_number = f"+{mobile_number}"

            customer = (
                self.db.query(CustomerModel)
                .filter(CustomerModel.mobile_number == mobile_number)
                .first()
            )
            if customer:
                main_logger.info(f"Customer found: {customer.id}")
            else:
                main_logger.warning(
                    f"No customer found with mobile number: {mobile_number}"
                )
            return customer
        except Exception as e:
            main_logger.error(f"Error fetching customer: {str(e)}")
            raise Exception(f"Database Error {str(e)}")

    def create_customer(self, customer_data: dict, mobile_number: str, business_phone_number: str = None):
        try:
            main_logger.info(
                f"Creating/updating customer with mobile number: {mobile_number}"
            )

            # Normalize mobile number for consistency
            if mobile_number:
                mobile_number = "".join(
                    c for c in mobile_number if c.isdigit() or c == "+"
                )
                
            # Find the business if business_phone_number is provided
            business = None
            if business_phone_number:
                main_logger.info(f"Looking up business with WhatsApp number: {business_phone_number}")
                # Remove the + prefix if present for consistency with how we store it
                if business_phone_number.startswith("+"):
                    business_phone_number = business_phone_number[1:]
                    
                from ..models.business_model import Business
                business = self.db.query(Business).filter(Business.whatsapp_number == business_phone_number).first()
                
                if business:
                    main_logger.info(f"Found business: {business.business_name} (ID: {business.id})")
                else:
                    main_logger.warning(f"No business found with WhatsApp number: {business_phone_number}")

            main_logger.info(f"Fetching customer with mobile number: {mobile_number}")
            customer = self.get_customer(mobile_number)

            if not customer:
                main_logger.warning(
                    f"No customer found with mobile number: {mobile_number}"
                )

                # Extract required fields with defaults to avoid KeyErrors
                new_customer = CustomerModel(
                    first_name=customer_data.get("firstNm", ""),
                    last_name=customer_data.get("lastNm", ""),
                    mobile_number=mobile_number,
                    email=customer_data.get("email", ""),
                    gender=customer_data.get("salutationCd", ""),
                    dplAccepted=customer_data.get("dplAccepted", False),
                    business_id=business.id if business else None
                )

                main_logger.debug(f"Creating new customer with data: {customer_data}")
                if business:
                    main_logger.info(f"Linking new customer to business: {business.business_name}")

                try:
                    self.db.add(new_customer)
                    self.db.commit()
                    self.db.refresh(new_customer)
                    main_logger.info(f"New customer created: {new_customer.id}")
                    return new_customer
                except Exception as db_error:
                    self.db.rollback()
                    main_logger.error(
                        f"DB error while inserting customer: {str(db_error)}"
                    )
                    raise Exception(f"Database insert error: {str(db_error)}")
            else:
                main_logger.info(f"Updating existing customer: {customer.id}")

                # Update fields if provided
                if customer_data.get("firstNm"):
                    customer.first_name = customer_data.get("firstNm")
                if customer_data.get("lastNm"):
                    customer.last_name = customer_data.get("lastNm")
                if customer_data.get("email"):
                    customer.email = customer_data.get("email")
                if customer_data.get("salutationCd"):
                    customer.gender = customer_data.get("salutationCd")
                    
                # Update business_id if we found a business and the customer isn't already linked
                if business and not customer.business_id:
                    customer.business_id = business.id
                    main_logger.info(f"Linking existing customer to business: {business.business_name}")

                try:
                    self.db.commit()
                    self.db.refresh(customer)
                    main_logger.info(f"Customer updated: {customer.id}")
                    return customer
                except Exception as db_error:
                    self.db.rollback()
                    main_logger.error(
                        f"DB error while updating customer: {str(db_error)}"
                    )
                    raise Exception(f"Database update error: {str(db_error)}")

        except Exception as e:
            self.db.rollback()
            main_logger.error(
                f"Database error while creating/updating customer: {str(e)}"
            )
            raise Exception(f"Database Error {str(e)}")

    def save_book_appointment(self, booking_details: dict, mobileNumber: str, business_phone_number: str = None):
        try:
            # Look for orderId (from TimeGlobe service) or order_id (fallback)
            order_id = booking_details.get('orderId') or booking_details.get('order_id')
            
            main_logger.info(f"Saving booking appointment for order_id: {order_id}")
            
            if not order_id:
                main_logger.error("No order ID found in booking details")
                main_logger.debug(f"Booking details: {booking_details}")
                raise Exception("No order ID found in booking details")
                
            customer = self.get_customer(mobileNumber)
            if not customer:
                main_logger.error("Customer not found while saving appointment.")
                raise Exception("Customer not found")

            site_cd = booking_details.get("siteCd")
            
            # Create the BookModel with the business phone number if provided
            book_appointment = BookModel(
                order_id=order_id,
                site_cd=site_cd,
                customer_id=customer.id,
                business_phone_number=business_phone_number,
                status=AppointmentStatus.BOOKED  # Set initial status as BOOKED
            )
            
            main_logger.info(f"Creating booking with business phone: {business_phone_number}")
            self.db.add(book_appointment)
            self.db.commit()
            self.db.refresh(book_appointment)
            main_logger.info(f"Booking appointment saved with ID: {book_appointment.id}")

            # Save booking details (positions)
            for position in booking_details.get("positions", []):
                main_logger.info(f"Processing booking position: {position}")
                try:
                    booking_detail = BookingDetail(
                        begin_ts=datetime.strptime(
                            position["beginTs"], "%Y-%m-%dT%H:%M:%S.%fZ"
                        ),
                        duration_millis=position["durationMillis"],
                        employee_id=position["employeeId"],
                        item_no=position["itemNo"],
                        item_nm=position.get("itemNm", ""), # Make itemNm optional
                        book_id=book_appointment.id,
                    )
                    self.db.add(booking_detail)
                    main_logger.info(f"Added booking detail for position: {position.get('ordinalPosition', 'unknown')}")
                except Exception as detail_error:
                    main_logger.error(f"Error saving booking detail: {str(detail_error)}")
                    main_logger.error(f"Position data: {position}")
                    # Continue with other positions even if one fails
                    continue

            self.db.commit()
            main_logger.info(f"Booking details saved for order_id: {order_id}")
            return book_appointment

        except Exception as e:
            self.db.rollback()
            main_logger.error(f"Database error while saving appointment: {str(e)}")
            raise Exception(f"Database error {str(e)}")

    def cancel_appointment(self, order_id: int) -> bool:
        """
        Cancel an appointment by updating its status
        
        Args:
            order_id: The order ID of the appointment to cancel
            
        Returns:
            bool: True if cancellation was successful, False otherwise
        """
        try:
            appointment = self.db.query(BookModel).filter(BookModel.order_id == order_id).first()
            if appointment:
                appointment.status = AppointmentStatus.CANCELLED
                appointment.cancelled_at = datetime.now()
                self.db.commit()
                main_logger.info(f"Successfully cancelled appointment with order_id: {order_id}")
                return True
            else:
                main_logger.warning(f"No appointment found with order_id: {order_id}")
                return False
        except Exception as e:
            self.db.rollback()
            main_logger.error(f"Error cancelling appointment: {str(e)}")
            return False

    def update_customer_email(self, mobile_number: str, email: str):
        """
        Update the email address for a customer.
        
        Args:
            mobile_number: The customer's mobile number
            email: The new email address
            
        Returns:
            CustomerModel: The updated customer record
        """
        try:
            main_logger.info(f"Updating email for customer with mobile number: {mobile_number}")
            
            # Normalize mobile number
            if not mobile_number.startswith("+"):
                mobile_number = f"+{mobile_number}"
                
            # Get the customer
            customer = self.get_customer(mobile_number)
            if not customer:
                main_logger.error(f"No customer found with mobile number: {mobile_number}")
                raise Exception("Customer not found")
                
            # Update the email
            customer.email = email
            self.db.commit()
            self.db.refresh(customer)
            
            main_logger.info(f"Successfully updated email for customer: {mobile_number}")
            return customer
            
        except Exception as e:
            self.db.rollback()
            main_logger.error(f"Database error while updating customer email: {str(e)}")
            raise Exception(f"Database error: {str(e)}")

    def update_customer_name(self, mobile_number: str, full_name: str, first_name: str = None, last_name: str = None):
        """
        Update the name fields for a customer.
        
        Args:
            mobile_number: The customer's mobile number
            full_name: The full name of the customer
            first_name: Optional first name
            last_name: Optional last name
            
        Returns:
            CustomerModel: The updated customer record
        """
        try:
            main_logger.info(f"Updating name for customer with mobile number: {mobile_number}")
            
            # Normalize mobile number
            if not mobile_number.startswith("+"):
                mobile_number = f"+{mobile_number}"
                
            # Get the customer
            customer = self.get_customer(mobile_number)
            if not customer:
                main_logger.error(f"No customer found with mobile number: {mobile_number}")
                raise Exception("Customer not found")
                
            # Update name fields
            if first_name:
                customer.first_name = first_name
            if last_name:
                customer.last_name = last_name
            
            self.db.commit()
            self.db.refresh(customer)
            
            main_logger.info(f"Successfully updated name for customer: {mobile_number}")
            return customer
            
        except Exception as e:
            self.db.rollback()
            main_logger.error(f"Database error while updating customer name: {str(e)}")
            raise Exception(f"Database error: {str(e)}")

    def update_customer_salutation(self, mobile_number: str, salutation_cd: str):
        """
        Update the salutation code for a customer.
        
        Args:
            mobile_number: The customer's mobile number
            salutation_cd: The salutation code ("na", "male", "female", "diverse")
            
        Returns:
            CustomerModel: The updated customer record
        """
        try:
            main_logger.info(f"Updating salutation for customer with mobile number: {mobile_number}")
            
            # Normalize mobile number
            if not mobile_number.startswith("+"):
                mobile_number = f"+{mobile_number}"
                
            # Get the customer
            customer = self.get_customer(mobile_number)
            if not customer:
                main_logger.error(f"No customer found with mobile number: {mobile_number}")
                raise Exception("Customer not found")
                
            # Update salutation
            customer.gender = salutation_cd
            self.db.commit()
            self.db.refresh(customer)
            
            main_logger.info(f"Successfully updated salutation for customer: {mobile_number}")
            return customer
            
        except Exception as e:
            self.db.rollback()
            main_logger.error(f"Database error while updating customer salutation: {str(e)}")
            raise Exception(f"Database error: {str(e)}")

    def update_customer_data_protection(self, mobile_number: str, dpl_accepted: bool):
        """
        Update the data protection acceptance status for a customer.
        
        Args:
            mobile_number: The customer's mobile number
            dpl_accepted: Whether data protection is accepted
            
        Returns:
            CustomerModel: The updated customer record
        """
        try:
            main_logger.info(f"Updating data protection for customer with mobile number: {mobile_number}")
            
            # Normalize mobile number
            if not mobile_number.startswith("+"):
                mobile_number = f"+{mobile_number}"
                
            # Get the customer
            customer = self.get_customer(mobile_number)
            if not customer:
                main_logger.error(f"No customer found with mobile number: {mobile_number}")
                raise Exception("Customer not found")
                
            # Update data protection status
            customer.dplAccepted = dpl_accepted
            self.db.commit()
            self.db.refresh(customer)
            
            main_logger.info(f"Successfully updated data protection for customer: {mobile_number}")
            return customer
            
        except Exception as e:
            self.db.rollback()
            main_logger.error(f"Database error while updating customer data protection: {str(e)}")
            raise Exception(f"Database error: {str(e)}")
