from sqlalchemy import Column, Integer, String, Date
from database.database import Base

class Apartment(Base):
    __tablename__ = "realoscan_data"  # Название твоей таблицы в MySQL

    ID = Column(Integer, primary_key=True, index=True)
    AdvantName = Column(String(255))
    Price = Column(Integer)
    LocalityName = Column(String(255))
    Link = Column(String(500))
    Date = Column("Date", Date)
    AdvertText = Column(String(2000))
    Activity = Column(Integer)
    RealityType = Column(Integer)
    RegionID = Column(Integer)
    DistrictId = Column(Integer)
    PragueLocalityDI = Column(Integer)
    Jmeno = Column(String(100))
    Telephone = Column(String(45))
    Email = Column(String(255))
    TelephoneServerCount = Column(Integer)
    EmailServerCount = Column(Integer)



    def to_dict(self):
        return {
            "id": self.ID,
            "AdvandName": self.AdvantName,
            "price": self.Price,
            "LocalityName": self.LocalityName,
            "link": self.Link,
            "date": self.Date,
            "AdvertText": self.AdvertText,
            "Activity": self.Activity,
            "RealityType": self.RealityType,
            "RegionID": self.RegionID,
            "DistrictId": self.DistrictId,
            "PragueLocalityId": self.PragueLocalityDI,
            "Jmeno": self.Jmeno,
            "Telefon": self.Telephone,
            "Email": self.Email,
            "TelephoneServerCount": self.TelephoneServerCount,
            "EmailServerCount": self.EmailServerCount
        }