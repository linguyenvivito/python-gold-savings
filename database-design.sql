-- SUPABASE DATABASE DESIGN --

CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- TABLE Profiles: User Profiles 
CREATE TABLE IF NOT EXISTS profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    full_name TEXT NULL,
    phone TEXT NULL,
    currency TEXT NULL DEFAULT 'VND',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NULL
);

-- Example of Profile Insertion:
-- INSERT INTO profiles (id, full_name, phone, currency) VALUES ('user-uuid', 'John Doe', '1234567890', 'USD');

CREATE TABLE IF NOT EXISTS gold_products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sku TEXT NOT NULL UNIQUE, -- # GOLD-RING-24K-001
    brand TEXT NOT NULL, --- # BrandName
    product_name TEXT NOT NULL, --- # RING, BAR, NECKLACE, BRACELET, EARRING, COIN, PENDANT, OTHER
    product_type TEXT NOT NULL, -- # RING, BAR, NECKLACE, BRACELET, EARRING, COIN, PENDANT, OTHER
    purity TEXT NOT NULL DEFAULT '24k', -- # 24k, 22k, 18k, 14k, 10k, 9k
    weight NUMERIC(18, 2) NOT NULL, -- # 9999.0
    weight_unit TEXT NOT NULL DEFAULT 'mace' -- # mace, gram, ounce
);

-- Example of gold_products Insertion:
-- INSERT INTO gold_products (sku, brand, product_name, product_type, purity, weight, weight_unit) 
-- VALUES ('GOLD-RING-24K-001', 'BrandName', 'ProductName', 'RING', '24k', 9999.0, 'mace');

CREATE TABLE IF NOT EXISTS stores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    address TEXT NULL,
    city TEXT NULL,
    phone TEXT NULL,
    email TEXT NULL,
    website TEXT NULL,
    latitude NUMERIC(10, 6) NULL,
    longitude NUMERIC(10, 6) NULL,
    opening_time TIME NULL,
    closing_time TIME NULL,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NULL
);

-- Example of stores Insertion:
-- INSERT INTO stores (name, address, city, phone, email, website, latitude, longitude, opening_time, closing_time) 
-- VALUES ('StoreName', '123 Main St', 'CityName', '1234567890', 'email@example.com', 'www.example.com', 10.123456, 20.123456, '09:00:00', '18:00:00');

CREATE TABLE IF NOT EXISTS scheduled_notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    scheduled_for TIMESTAMPTZ NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    dispatched_at TIMESTAMPTZ NULL
);

-- Example of scheduled_notifications Insertion:
-- INSERT INTO scheduled_notifications (title, message, scheduled_for) 
-- VALUES ('Notification Title', 'Notification Message', '2024-06-01 10:00:00');

CREATE TABLE IF NOT EXISTS gold_accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    account_name TEXT NULL,
    target_amount NUMERIC(18, 2) NULL,
    target_weight NUMERIC(18, 2) NULL,
    target_weight_unit TEXT NULL DEFAULT 'mace',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NULL
);

-- Example of gold_accounts Insertion:
-- INSERT INTO gold_accounts (user_id, account_name, target_amount, target_weight, target_weight_unit) 
-- VALUES ('user-uuid', 'My Gold Account', 10000.0, 10.0, 'mace');

CREATE TABLE IF NOT EXISTS gold_prices (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    gold_product_id UUID NOT NULL REFERENCES gold_products(id) ON DELETE CASCADE,
    store_id UUID NOT NULL REFERENCES stores(id) ON DELETE CASCADE,
    effective_at TIMESTAMPTZ NOT NULL,
    buy_price NUMERIC(18, 2) NOT NULL,
    sell_price NUMERIC(18, 2) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Example of gold_prices Insertion:
-- INSERT INTO gold_prices (gold_product_id, store_id, effective_at, buy_price, sell_price) 
-- VALUES ('gold-product-uuid', 'store-uuid', '2024-06-01 10:00:00', 1000.0, 1100.0);

CREATE TABLE IF NOT EXISTS transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID NOT NULL REFERENCES gold_accounts(id) ON DELETE CASCADE,
    gold_product_id UUID NOT NULL REFERENCES gold_products(id) ON DELETE CASCADE,
    store_id UUID NOT NULL REFERENCES stores(id) ON DELETE CASCADE,
    transaction_type TEXT NOT NULL,
    quantity NUMERIC(18, 2) NOT NULL,
    executed_price NUMERIC(18, 2) NOT NULL,
    cash_amount NUMERIC(18, 2) NOT NULL,
    fee NUMERIC(18, 2) NULL DEFAULT 0.0,
    note TEXT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Example of transactions Insertion:
-- INSERT INTO transactions (account_id, transaction_type, cash_amount, gold_price, unit, note) 
-- VALUES ('account-uuid', 'buy', 1000.0, 50.0, 'mace', 'Initial deposit');

CREATE TABLE IF NOT EXISTS notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    scheduled_notification_id UUID NULL REFERENCES scheduled_notifications(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    read_at TIMESTAMPTZ NULL
);

-- Example of notifications Insertion:
-- INSERT INTO notifications (user_id, title, message, scheduled_notification_id) 
-- VALUES ('user-uuid', 'Notification Title', 'Notification Message', 'scheduled-notification-uuid');

CREATE TABLE IF NOT EXISTS notification_push_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    provider TEXT NOT NULL DEFAULT 'expo',
    token TEXT NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Example of notification_push_tokens Insertion:
-- INSERT INTO notification_push_tokens (user_id, provider, token) 
-- VALUES ('user-uuid', 'expo', 'push-token-uuid');

CREATE TABLE IF NOT EXISTS favourite_stores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    store_id UUID NOT NULL REFERENCES stores(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (user_id, store_id)
);

-- Example of favourite_stores Insertion:
-- INSERT INTO favourite_stores (user_id, store_id) 
-- VALUES ('user-uuid', 'store-uuid');

CREATE TABLE IF NOT EXISTS reminders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    account_id UUID NOT NULL REFERENCES gold_accounts(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    reminder_type TEXT NOT NULL DEFAULT 'one-time', -- # one-time, recurring
    reminder_time TIMESTAMPTZ NOT NULL,
    recurrence_pattern TEXT NULL, -- # daily, weekly, monthly, yearly
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Example of reminders Insertion:
-- INSERT INTO reminders (user_id, account_id, title, message, reminder_type, reminder_time, recurrence_pattern) 
-- VALUES ('user-uuid', 'account-uuid', 'Reminder Title', 'Reminder Message', 'one-time', '2024-06-01 10:00:00', NULL);

-- CREATE OR REPLACE VIEW transaction_store AS
-- SELECT DISTINCT ON (gp.store_id, gp.gold_product_id)
--     gp.id AS gold_price_id,
--     s.id AS store_id,
--     s.name AS store_name,
--     s.address,
--     s.city,
--     s.phone,
--     s.latitude,
--     s.longitude,
--     p.id AS gold_product_id,
--     p.sku,
--     p.brand,
--     p.product_name,
--     p.product_type,
--     p.purity,
--     p.weight,
--     p.weight_unit,
--     gp.price_time,
--     gp.buy_price,
--     gp.sell_price
-- FROM gold_prices gp
-- JOIN stores s ON s.id = gp.store_id
-- JOIN gold_products p ON p.id = gp.gold_product_id
-- WHERE s.active = TRUE
-- ORDER BY gp.store_id, gp.gold_product_id, gp.price_time DESC;

CREATE INDEX IF NOT EXISTS idx_gold_accounts_user
    ON gold_accounts (user_id);

CREATE INDEX IF NOT EXISTS idx_gold_prices_product_store_effective
    ON gold_prices (gold_product_id, store_id, effective_at DESC);

CREATE INDEX IF NOT EXISTS idx_gold_prices_store_effective
    ON gold_prices (store_id, effective_at DESC);

CREATE INDEX IF NOT EXISTS idx_transactions_account_created
    ON transactions (account_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_transactions_product_created
    ON transactions (gold_product_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_transactions_store_created
    ON transactions (store_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_scheduled_notifications_pending_time
    ON scheduled_notifications (status, scheduled_for);

CREATE INDEX IF NOT EXISTS idx_notifications_user_created
    ON notifications (user_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_notifications_scheduled
    ON notifications (scheduled_notification_id);

CREATE INDEX IF NOT EXISTS idx_notification_push_tokens_user
    ON notification_push_tokens (user_id);

CREATE INDEX IF NOT EXISTS idx_favourite_stores_store
    ON favourite_stores (store_id);

CREATE INDEX IF NOT EXISTS idx_reminders_user_time
    ON reminders (user_id, reminder_time);

CREATE INDEX IF NOT EXISTS idx_reminders_account_time
    ON reminders (account_id, reminder_time);

--- PROCESSES FOR THIS APP
--- 1. User Registration and Profile Creation
-- When a new user registers, a profile is automatically created in the profiles table with the user's UUID from the auth.users table. The profile can be updated later with additional information such as full name, phone number, and preferred currency.
--- 2. Gold Product Management
-- Admins can add new gold products to the gold_products table, specifying details such as SKU, brand, product name, product type, purity, weight, and weight unit. This allows the system to keep track of various gold products available in the market.
--- 3. Store Management
-- Admins can add new stores to the stores table, including details such as name, address, city, phone number, email, website, location coordinates (latitude and longitude), opening and closing times, and active status. This enables users to find and interact with different stores.
--- 4. Gold Price Tracking
-- The system tracks gold prices for different products at various stores. Admins can insert price records into the gold_prices table, including the gold product ID, store ID, price time, buy price, and sell price. This allows users to view historical and current gold prices for informed decision-making.
--- 5. Gold Account Management
-- Created a default gold account for each user when they register. Users can create and manage their gold accounts in the gold_accounts table. Each account is linked to a user profile and can have a target amount, target weight, and target weight unit. Users can activate or deactivate their accounts as needed.
-- Users can create and manage their gold accounts in the gold_accounts table. Each account is linked to a user profile and can have a target amount, target weight, and target weight unit. Users can activate or deactivate their accounts as needed.
--- 6. Transaction Management
-- Users can record transactions related to their gold accounts in the transactions table. Each transaction includes details such as account ID, transaction type (buy/sell), cash amount, gold price, unit, and an optional note. This allows users to keep track of their gold-related financial activities.
--- 7. Notification System
-- The system includes a notification system to keep users informed about important events. Notifications can be scheduled and managed through the notifications table.
--- 8. Favourite Stores
-- Users can mark stores as favourites in the favourite_stores table. This allows users to quickly access their preferred stores and receive updates or notifications related to those stores.
--- 9. Reminders
-- Users can set reminders in the reminders table for important events related to their gold accounts. Reminders can be one-time or recurring, and users can specify the reminder time and recurrence pattern. This helps users stay organized and manage their gold-related activities effectively.
--- 10. Push Notifications
-- The system supports push notifications through the notification_push_tokens table. Users can register their device tokens