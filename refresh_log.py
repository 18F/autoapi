from datetime import datetime, timedelta

from flask_sqlalchemy import SQLAlchemy

import config

db = SQLAlchemy()


class AutoapiTableRefreshLog(db.Model):
    __tablename__ = 'autoapi_table_refresh_log'

    id = db.Column(db.Integer, primary_key=True)
    complete = db.Column(db.Boolean, nullable=False, default=False)
    begun_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    complete_at = db.Column(db.DateTime)
    err_msg = db.Column(db.String)

    def close(self):
        self.complete_at = datetime.now()
        self.complete = True

    @classmethod
    def start(cls):
        log_entry = cls()
        db.session.add(log_entry)
        db.session.commit()
        return log_entry.id

    @classmethod
    def stop_hung(cls):
        cutoff_time = datetime.now() - timedelta(
            seconds=config.REFRESH_TIMEOUT_SECONDS)
        for entry in db.session.query(cls).filter_by(complete=False) \
            .filter(cls.begun_at < cutoff_time):
            entry.err_msg = 'Ran too long, presumed dead'
            entry.close()
        db.session.commit()

    @classmethod
    def refresh_underway(cls):
        cls.stop_hung()
        return db.session.query(AutoapiTableRefreshLog).filter_by(
            complete=False).first()


def stop(id, err_msg=None):
    log_entry = db.session.query(AutoapiTableRefreshLog).get(id)
    log_entry.close()
    log_entry.err_msg = err_msg
    db.session.commit()
