from db import get_connection
from psycopg2 import errors


def query(sql, params=None):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            return [dict(row) for row in cur.fetchall()] if cur.description else []


def execute(sql, params=None):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            return cur.fetchone() if cur.description else None


def lookup(table, id_col, name_col):
    allowed = {
        ('categories','category_id','category_name'),
        ('manufacturers','manufacturer_id','manufacturer_name'),
        ('suppliers','supplier_id','supplier_name'),
        ('order_statuses','status_id','status_name'),
        ('users','user_id','full_name'),
        ('products','product_id','product_name'),
    }
    if (table,id_col,name_col) not in allowed:
        raise ValueError('Недопустимый справочник')
    return query(f'SELECT {id_col}, {name_col} FROM {table} ORDER BY {name_col}')



def fetch_clients():
    """Return only users with the client role for the order form."""
    return query(
        "SELECT u.user_id, u.full_name FROM users u "
        "JOIN roles r ON r.role_id = u.role_id "
        "WHERE r.role_name = %s ORDER BY u.full_name",
        ("client",),
    )


def fetch_products(search='', category_id=None, sort_field='product_name', sort_dir='ASC'):
    allowed={'product_name','price','quantity_in_stock','discount_percent'}
    if sort_field not in allowed: sort_field='product_name'
    sort_dir='DESC' if str(sort_dir).upper()=='DESC' else 'ASC'
    sql='''SELECT p.product_id,p.product_name,p.price,p.quantity_in_stock,p.discount_percent,p.image_path,
                  p.category_id,p.manufacturer_id,p.supplier_id,c.category_name,m.manufacturer_name,s.supplier_name,
                  ROUND((p.price*(1-p.discount_percent/100.0))::numeric,2) AS final_price
           FROM products p JOIN categories c USING(category_id)
           JOIN manufacturers m USING(manufacturer_id) JOIN suppliers s USING(supplier_id)
           WHERE (%s='' OR p.product_name ILIKE %s OR c.category_name ILIKE %s OR m.manufacturer_name ILIKE %s)
             AND (%s IS NULL OR p.category_id=%s)
           ORDER BY p.{} {}, p.product_id ASC'''.format(sort_field, sort_dir)
    return query(sql,(search, f'%{search}%',f'%{search}%',f'%{search}%',category_id,category_id))


def save_product(data, product_id=None):
    if product_id is None:
        execute('''INSERT INTO products(product_name,category_id,manufacturer_id,supplier_id,price,quantity_in_stock,discount_percent,image_path)
                   VALUES(%(product_name)s,%(category_id)s,%(manufacturer_id)s,%(supplier_id)s,%(price)s,%(quantity_in_stock)s,%(discount_percent)s,%(image_path)s)''',data)
    else:
        execute('''UPDATE products SET product_name=%(product_name)s,category_id=%(category_id)s,manufacturer_id=%(manufacturer_id)s,
                   supplier_id=%(supplier_id)s,price=%(price)s,quantity_in_stock=%(quantity_in_stock)s,
                   discount_percent=%(discount_percent)s,image_path=%(image_path)s WHERE product_id=%(product_id)s''', {**data,'product_id':product_id})


def delete_product(product_id):
    execute('DELETE FROM products WHERE product_id=%s',(product_id,))


def fetch_orders():
    return query('''SELECT o.order_id,o.article,o.product_id,o.client_id,o.status_id,o.pickup_address,o.order_date,o.issue_date,
                           s.status_name,p.product_name,u.full_name AS client_name
                    FROM orders o JOIN order_statuses s USING(status_id)
                    JOIN products p USING(product_id) JOIN users u ON u.user_id=o.client_id
                    ORDER BY o.order_date DESC,o.order_id DESC''')


def save_order(data, order_id=None):
    if order_id is None:
        execute('''INSERT INTO orders(article,product_id,client_id,status_id,pickup_address,order_date,issue_date)
                   VALUES(%(article)s,%(product_id)s,%(client_id)s,%(status_id)s,%(pickup_address)s,%(order_date)s,%(issue_date)s)''',data)
    else:
        execute('''UPDATE orders SET article=%(article)s,product_id=%(product_id)s,client_id=%(client_id)s,status_id=%(status_id)s,
                   pickup_address=%(pickup_address)s,order_date=%(order_date)s,issue_date=%(issue_date)s WHERE order_id=%(order_id)s''', {**data,'order_id':order_id})


def delete_order(order_id):
    execute('DELETE FROM orders WHERE order_id=%s',(order_id,))
