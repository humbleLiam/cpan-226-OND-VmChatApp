from sqlalchemy import create_engine, Column, Integer , String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

Base = declarative_base()

class Contact(Base):
    __tablename__ = 'contacts'
    id = Column(Integer, primary_key=True)
    ip_address = Column(String , unique=True, nullable=False)
    name= Column(String , default="Unknown")
    last_seen = Column(DateTime, default=datetime.now)

    messages = relationship("Message", back_populates="contact",cascade="all,delete-orphan")
    def __repr__(self):
        return f"<Contact(ip='{self.ip_address}',name ='{self.name}')>"
    
class Message(Base):
    __tablename__='messages'
    id = Column(Integer,primary_key=True)
    contact_id = Column(Integer, ForeignKey('contacts.id'), nullable=False)
    message_text = Column(String, nullable=False)
    sender = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.now, nullable=False)

    contact = relationship("Contact",back_populates="messages")

    def __repr__(self):
        return f"Message(sender='{self.sender}', text='{self.message_text[:20]}...')"
    
class ChatDatabase:
    def __init__(self, db_path="chat_history.db"):
        self.db_path = db_path
        self.engine = create_engine(f'sqlite:///{db_path}', echo=False)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def add_contact(self,ip_address,name="Unknow"):
        contact = self.session.query(Contact).filter_by(ip_address=ip_address).first()

        if contact:
            contact.name = name
            contact.last_seen = datetime.now()
        else:
            contact = Contact(ip_address = ip_address, name = name)
            self.session.add(contact)
        
        self.session.commit()
        return contact
    def get_contact(self,ip_address):
        return self.session.query(Contact).filter_by(ip_address=ip_address).first()
    
    def get_all_contacts(self):
        return self.session.query(Contact).order_by(Contact.last_seen.desc()).all()
    def update_contact_name(self,ip_address, name):
        contact = self.get_contact(ip_address)
        if contact:
            contact.name = name
            self.session.commit()
            return True
        return False
    def delete_contact(self, ip_address):
        contact = self.get_contact(ip_address)
        if contact:
            self.session.delete(contact)
            self.session.commit()
            return True
        return False
    
    def add_message(self, ip_address, message_text, sender):
        contact = self.get_contact(ip_address)
        if not contact:
            contact = self.add_contact(ip_address)
        
        contact.last_seen = datetime.now()

        message = Message (
            contact_id = contact.id,
            message_text=message_text,
            sender = sender,
            timestamp= datetime.now()

        )
        self.session.add(message)
        self.session.commit()
        return message
    
    def get_messages(self,ip_address, limit=None):
        contact = self.get_contact(ip_address)
        if not contact:
            return[]
        
        query = self.session.query(Message).filter_by(contact_id=contact.id).order_by(Message.timestamp)
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    def get_recent_messages(self, ip_address , count=50):
        contact = self.get_contact(ip_address)
        if not contact:
            return []
        
        return self.session.query(Message)\
        .filter_by(contact_id=contact.id)\
        .order_by(Message.timestamp.desc())\
        .limit(count)\
        .all()[::-1]
    
    def delete_all_messages(self, ip_address):
        contact = self.get_contact(ip_address)
        if contact:
            self.session.query(Message).filter_by(contact_id =contact.id).delete()
            self.session.commit()
            return True
        
        return False
    
    def close(self):
        self.session.close()