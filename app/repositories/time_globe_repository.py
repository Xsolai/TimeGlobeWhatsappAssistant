from sqlalchemy.orm import Session
from ..models.customer_model import CustomerModel
from ..models.booked_appointment import BookModel
from ..models.booking_detail import BookingDetail
from datetime import datetime


class TimeGlobeRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_customer(self, mobile_number: str) -> CustomerModel:
        try:
            customer = (
                self.db.query(CustomerModel)
                .filter(CustomerModel.mobile_number == mobile_number)
                .first()
            )
            return customer
        except Exception as e:
            raise Exception(f"Database Error {str(e)}")

    def create_customer(self, customer_data: dict, mobile_number: str):
        try:
            customer = self.get_customer(mobile_number)
            print("****", customer)
            if not customer:
                new_cusomter = CustomerModel(
                    first_name=customer_data.get("firstNm"),
                    last_name=customer_data.get("lastNm"),
                    mobile_number=mobile_number,
                    email=customer_data.get("email"),
                    gender=customer_data.get("salutationCd"),
                )
                self.db.add(new_cusomter)
                self.db.commit()
                self.db.refresh(new_cusomter)
                return new_cusomter

        except Exception as e:
            self.db.rollback()
            print("Database exception ==>>", str(e))
            raise Exception(f"Database Error {str(e)}")

    def save_book_appointement(self, booking_details: dict):
        try:
            customer = self.get_customer(booking_details.get("mobile_number"))
            site_cd = booking_details.get("siteCd")
            book_appointement = BookModel(
                order_id=booking_details.get("order_id"),
                site_cd=site_cd,
                customer_id=customer.id,
            )
            self.db.add(book_appointement)
            self.db.commit()

            for position in booking_details.get("positions", []):
                print(position)
                booking_detail = BookingDetail(
                    begin_ts=datetime.strptime(
                        position["beginTs"], "%Y-%m-%dT%H:%M:%S.%fZ"
                    ),
                    duration_millis=position["durationMillis"],
                    employee_id=position["employeeId"],
                    item_no=position["itemNo"],
                    item_nm=position["itemNm"],
                    book_id=book_appointement.id,
                )
                self.db.add(booking_detail)

            self.db.commit()
        except Exception as e:
            print(f"exception==>> {str(e)}")
            self.db.rollback()
            raise Exception(f"Database error {str(e)}")

    def delete_booking(self, order_id: int):
        try:
            booking = (
                self.db.query(BookModel).filter(BookModel.order_id == order_id).first()
            )
            if not booking:
                raise Exception("Booking not found")
            self.db.query(BookingDetail).filter(
                BookingDetail.book_id == booking.id
            ).delete()
            self.db.delete(booking)
            self.db.commit()

        except Exception as e:
            self.db.rollback()
            raise Exception(f"Database error: {str(e)}")
