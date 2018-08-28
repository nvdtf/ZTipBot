import datetime
import logging
from peewee import *

db = SqliteDatabase('ztipbot.db')

logging.basicConfig(filename='bot.log', level=logging.INFO)

logger = logging.getLogger("bot-db")

logger.info('testing')

def get_user_by_id(user_id):
    try:
        user = User.get(user_id=user_id)
        return user
    except User.DoesNotExist:
        # logger.debug('user %s does not exist !', user_id)
        return None


def get_user_by_wallet_address(address):
    try:
        user = User.get(wallet_address=address)
        return user
    except User.DoesNotExist:
        # logger.debug('wallet %s does not exist !', address)
        return None


def get_transaction_status_by_txid(txid):
    try:
        transaction = Transaction.get(wallet_txid=txid)
        return transaction.status
    except Transaction.DoesNotExist:
        logger.info('transaction %s does not exist !', txid)
        return 'DOESNT_EXIST'


def get_top_users(count):
    users = User.select().where(User.tipped_amount > 0).order_by(User.tipped_amount.desc()).limit(count)
    return_data = []
    for idx, user in enumerate(users):
        return_data.append({'index': idx + 1, 'name': user.user_name, 'amount': user.tipped_amount})
    return return_data


def create_user(user_id, user_name, wallet_address):
    user = User(user_id=user_id,
                user_name=user_name,
                wallet_address=wallet_address,
                balance=0.0,
                tipped_amount=0.0,
                created=datetime.datetime.now()
                )
    user.save()
    return user


def create_withdraw_transaction(wallet_txid, amount, from_user):
    with db.atomic() as transaction:
        try:
            withdraw_transaction = Transaction(type='WITHDRAW',
                                               wallet_txid=wallet_txid,
                                               amount=amount,
                                               to_user=None,
                                               from_user=from_user,
                                               transaction_time=None,
                                               raw_tx_rpc=None,
                                               status='SENT',
                                               created=datetime.datetime.now()
                                               )
            from_user.balance -= amount
            from_user.save()
            withdraw_transaction.save()
            return True
        except Exception as e:
            db.rollback()
            logger.exception(e)
            return False


def create_deposit_transaction(wallet_txid, amount, to_user,
                               transaction_time, raw_tx_rpc, status):
    with db.atomic() as transaction:
        try:
            transaction_type = 'DEPOSIT'
            if to_user is None:
                transaction_type = 'DEPOSIT_UNKNOWN'
            deposit_transaction = Transaction(type=transaction_type,
                                              wallet_txid=wallet_txid,
                                              amount=amount,
                                              to_user=to_user,
                                              from_user=None,
                                              transaction_time=transaction_time,
                                              raw_tx_rpc=raw_tx_rpc,
                                              status=status,
                                              created=datetime.datetime.now()
                                              )
            if to_user is not None and status is not 'UNCONFIRMED':
                to_user.balance += float(amount)
                to_user.save()
            deposit_transaction.save()
            return True
        except Exception as e:
            db.rollback()
            logger.exception(e)
            return False


def confirm_transaction(txid, raw_tx_rpc):
    with db.atomic() as transaction:
        try:
            transaction_row = Transaction.get(wallet_txid=txid)
            transaction_row.status = 'CONFIRMED'
            transaction_row.raw_tx_rpc = raw_tx_rpc
            if transaction_row.to_user is not None:
                transaction_row.to_user.balance += float(transaction_row.amount)
                transaction_row.to_user.save()
            transaction_row.save()
            return True
        except Exception as e:
            db.rollback()
            logger.exception(e)
            return False


def move_funds(user, amount, target_user):
    with db.atomic() as transaction:
        try:
            tip_row = Tip(
                from_user=user,
                to_user=target_user,
                amount=amount,
                timestamp=datetime.datetime.now()
            )
            user.balance -= amount
            user.tipped_amount += amount
            target_user.balance += amount
            tip_row.save()
            user.save()
            target_user.save()
            return True
        except Exception as e:
            db.rollback()
            logger.exception(e)
            return False


class User(Model):
    user_id = CharField()
    user_name = CharField()
    wallet_address = CharField()
    balance = FloatField()
    tipped_amount = FloatField()
    created = DateField()

    class Meta:
        database = db


class Tip(Model):
    from_user = ForeignKeyField(User, related_name='outgoing_tips')
    to_user = ForeignKeyField(User, related_name='incoming_tips')
    amount = FloatField()
    timestamp = DateField()

    class Meta:
        database = db


class Transaction(Model):
    type = CharField()
    wallet_txid = DateField()
    amount = FloatField()
    to_user = ForeignKeyField(User, related_name='incoming_transactions', null=True)
    from_user = ForeignKeyField(User, related_name='outgoing_transactions', null=True)
    transaction_time = DateField(null=True)
    raw_tx_rpc = CharField(null=True)
    status = CharField()
    created = DateField()

    class Meta:
        database = db


def create_db():
    db.connect()
    db.create_tables([User, Transaction, Tip], safe=True)


create_db()
