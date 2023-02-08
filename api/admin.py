from argparse import ArgumentParser
from adventure_api.setup import get_conn, setup_database

parser = ArgumentParser(
    description='A command-line utility tool for managing the adventure game.')

subparsers = parser.add_subparsers(help='The management tools available.')
db_parser = subparsers.add_parser('db', help='Handles the database management.')
db_parser.add_argument(
    'action', choices=['flush'],
    help='The action to do on the database.')
db_parser.set_defaults(handler='db')

user_parser = subparsers.add_parser(
    'users', help='Handles the user management.')
user_parser.add_argument(
    'action', choices=['list', 'set_admin', 'delete'],
    help='The action to do on the users.')
user_parser.add_argument(
    '-e',
    '--email',
    type=str,
    help='The email of what you want to action.')
user_parser.set_defaults(handler='users')

if __name__ == '__main__':
    args = parser.parse_args()
    driver, conn = get_conn()
    if args.handler == 'db':
        if args.action == 'flush':
            print('Are you sure you wish to do this action? [Y/n]')
            x = input()
            if x != 'y' and x != 'yes':
                exit(0)
            try:
                with conn.cursor() as cur:
                    cur.execute('DROP TABLE users')
                conn.commit()
                setup_database()
            finally:
                conn.close()
    elif args.handler == 'users':
        if args.action == 'list':
            try:
                with conn.cursor() as cur:
                    cur.execute(
                        'SELECT id, email, is_admin, name, x, z, state, additional_data FROM users')
                    for user in cur.fetchall():
                        print(
                            f'{user[0]} | {user[1]} | {user[2]} | {user[3]} | {user[4]} | {user[5]} | {user[6]} | {user[7]}')
            finally:
                conn.close()
        elif args.action == 'set_admin':
            if not args.email:
                user_parser.print_help()
                exit(1)
            try:
                with conn.cursor() as cur:
                    cur.execute(
                        'UPDATE users SET is_admin = %s WHERE email = %s', [
                            True,
                            args.email])
                conn.commit()
            finally:
                conn.close()
            print(f'Set {args.email} to an admin')
        elif args.action == 'delete':
            if not args.email:
                user_parser.print_help()
                exit(1)
            try:
                with conn.cursor() as cur:
                    cur.execute(
                        'UPDATE users SET name = %s, x = %s, z = %s, state = %s, additional_data = %s WHERE email = %s', [
                            None, 0, 0, 'intro', '{}', args.email])
                conn.commit()
            finally:
                conn.close()
            print(f'Reset {args.email}')
