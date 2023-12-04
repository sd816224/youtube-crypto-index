import logging
from pg8000.native import Connection, DatabaseError, InterfaceError


logger = logging.getLogger('db_connection')
logger.setLevel(logging.INFO)


def get_connection(database_credentials):
    '''
    Gets connections to the RDS database(leee-total-db)


    Parameters
    ----------
    database_credentials (from the get_credentials util),
    which is a dictionary consisting of:
        user
        host
        database
        port
        password

    Raises
    ------
    DatabaseError: Will return an error message showing what is missing.
        i.e. if the password is wrong, the error message will state password
        authentication has failed.
    InterfaceError:

    Returns
    -------
    A successful pg8000 connection object will be returned.
    '''
    try:
        user = database_credentials['RDS_USERNAME']
        host = database_credentials['RDS_HOSTNAME']
        database = database_credentials['DS_DB_NAME']
        port = database_credentials['RDS_PORT']
        password = database_credentials['RDS_PASSWORD']

        conn = Connection(user, host, database, port, password, timeout=5)
        logger.info('Connection to database has been established.')
        return conn
    except DatabaseError as db:
        logger.error(f"pg8000 - an error has occured: {db.args[0]['M']}")
        raise db
    except InterfaceError as ie:
        logger.error(f'pg8000 - an error has occured: \n"{ie}"')
        raise ie
    except Exception as exc:
        logger.error(
            'An error has occured when attempting to connect to the database.')
        raise exc
