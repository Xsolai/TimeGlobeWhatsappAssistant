import logging
from sqlalchemy.orm import Session
from ..models.booked_appointment import BookModel
from ..models.customer_model import CustomerModel
from ..models.booking_detail import BookingDetail
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

    def create_customer(self, customer_data: dict, mobile_number: str):
        try:
            main_logger.info(
                f"Creating/updating customer with mobile number: {mobile_number}"
            )

            # Normalize mobile number for consistency
            if mobile_number:
                mobile_number = "".join(
                    c for c in mobile_number if c.isdigit() or c == "+"
                )

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
                    gender=customer_data.get("salutationCd", "M"),
                )

                main_logger.debug(f"Creating new customer with data: {customer_data}")

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

    def save_book_appointment(self, booking_details: dict):
        try:
            main_logger.info(
                f"Saving booking appointment for order_id: {booking_details.get('orderId')}"
            )
            customer = self.get_customer(booking_details.get("mobileNumber"))
            if not customer:
                main_logger.error("Customer not found while saving appointment.")
                raise Exception("Customer not found")

            site_cd = booking_details.get("siteCd")
            book_appointment = BookModel(
                order_id=booking_details.get("orderId"),
                site_cd=site_cd,
                customer_id=customer.id,
            )
            self.db.add(book_appointment)
            self.db.commit()
            main_logger.info(
                f"Booking appointment saved with ID: {book_appointment.id}"
            )

            # for position in booking_details.get("positions", []):
            #     main_logger.info(f"Processing booking position: {position}")
            #     booking_detail = BookingDetail(
            #         begin_ts=datetime.strptime(
            #             position["beginTs"], "%Y-%m-%dT%H:%M:%S.%fZ"
            #         ),
            #         duration_millis=position["durationMillis"],
            #         employee_id=position["employeeId"],
            #         item_no=position["itemNo"],
            #         item_nm=position["itemNm"],
            #         book_id=book_appointment.id,
            #     )
            #     self.db.add(booking_detail)

            # self.db.commit()
            main_logger.info(
                f"Booking details saved for order_id: {booking_details.get('orderId')}"
            )

        except Exception as e:
            self.db.rollback()
            main_logger.error(f"Database error while saving appointment: {str(e)}")
            raise Exception(f"Database error {str(e)}")

    def delete_booking(self, order_id: int):
        try:
            main_logger.info(f"Deleting booking for order_id: {order_id}")
            booking = (
                self.db.query(BookModel).filter(BookModel.order_id == order_id).first()
            )

            if not booking:
                main_logger.warning(f"No booking found with order_id: {order_id}")
                raise Exception("Booking not found")

            self.db.query(BookingDetail).filter(
                BookingDetail.book_id == booking.id
            ).delete()
            self.db.delete(booking)
            self.db.commit()
            main_logger.info(f"Booking deleted successfully for order_id: {order_id}")

        except Exception as e:
            self.db.rollback()
            main_logger.error(f"Database error while deleting booking: {str(e)}")
            # raise Exception(f"Database error: {str(e)}")
