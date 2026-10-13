-- Выполнить один раз в Query Tool базы shoe_store, если колонки article ещё нет.
ALTER TABLE orders ADD COLUMN IF NOT EXISTS article VARCHAR(50);
UPDATE orders SET article = 'ORD-' || LPAD(order_id::text, 4, '0') WHERE article IS NULL;
ALTER TABLE orders ALTER COLUMN article SET NOT NULL;
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname='orders_article_key') THEN
        ALTER TABLE orders ADD CONSTRAINT orders_article_key UNIQUE(article);
    END IF;
END $$;
