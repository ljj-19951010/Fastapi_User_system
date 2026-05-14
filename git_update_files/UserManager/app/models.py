from typing import Optional

from sqlalchemy import ForeignKeyConstraint, Index, Integer, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class User(Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(255), nullable=False, comment='用户名')
    password: Mapped[str] = mapped_column(String(255), nullable=False, comment='密码')
    email: Mapped[str] = mapped_column(String(255), nullable=False, comment='邮箱')
    is_supper: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("'0'"), comment='是否超级用户')
    is_active: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("'1'"), comment='是否激活')

    user_info: Mapped[list['UserInfo']] = relationship('UserInfo', back_populates='user')


class UserInfo(Base):
    __tablename__ = 'user_info'
    __table_args__ = (
        ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE', name='user_id'),
        Index('user_id', 'user_id')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, comment='姓名')
    gender: Mapped[str] = mapped_column(String(255), nullable=False, comment='性别')
    birthday: Mapped[Optional[str]] = mapped_column(String(255), comment='生日')
    phone: Mapped[Optional[str]] = mapped_column(String(255), comment='手机号')
    address: Mapped[Optional[str]] = mapped_column(String(255), comment='地址')
    user_id: Mapped[Optional[int]] = mapped_column(Integer, comment='外键')

    user: Mapped[Optional['User']] = relationship('User', back_populates='user_info')
