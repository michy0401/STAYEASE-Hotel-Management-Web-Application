-- ============================================================================
--  StayEase — MySQL 8 Database Schema
--  Engine: InnoDB | Charset: utf8mb4 | Collation: utf8mb4_unicode_ci
-- ============================================================================

CREATE DATABASE IF NOT EXISTS stayease
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE stayease;

-- ----------------------------------------------------------------------------
--  USERS
--  role distinguishes front-desk staff (reservation agents) from managers
--  (room editors, reports). password_hash stores only the result of a
--  one-way hashing algorithm. Plain-text passwords must never be persisted.
-- ----------------------------------------------------------------------------
CREATE TABLE users (
    id            INT          NOT NULL AUTO_INCREMENT,
    username      VARCHAR(50)  NOT NULL,
    email         VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name     VARCHAR(100)     NULL,
    role          ENUM('staff','manager') NOT NULL DEFAULT 'staff',
    created_at    TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at    TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP
                                        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT pk_users          PRIMARY KEY (id),
    CONSTRAINT uq_users_username UNIQUE (username),
    CONSTRAINT uq_users_email    UNIQUE (email)
);

-- ----------------------------------------------------------------------------
--  ROOMS
--  Represents a physical hotel room. is_available controls whether the room
--  can be booked. status tracks the real-time housekeeping state; a change
--  from 'occupied' to 'available' is broadcast over WebSocket to all
--  connected staff dashboards so they know a room needs cleaning.
-- ----------------------------------------------------------------------------
CREATE TABLE rooms (
    id            INT            NOT NULL AUTO_INCREMENT,
    room_number   VARCHAR(10)    NOT NULL,
    room_type     ENUM(
                    'single',
                    'double',
                    'suite',
                    'family'
                  )              NOT NULL DEFAULT 'single',
    floor         INT            NOT NULL DEFAULT 1,
    price_per_night DECIMAL(8, 2) NOT NULL,
    capacity      INT            NOT NULL DEFAULT 1,   -- max number of guests
    description   TEXT               NULL,
    status        ENUM(
                    'available',    -- clean, ready to receive guests
                    'occupied',     -- currently hosting a guest
                    'cleaning',     -- checked out, awaiting housekeeping
                    'maintenance'   -- under repair, cannot be booked
                  )              NOT NULL DEFAULT 'available',
    created_at    TIMESTAMP      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at    TIMESTAMP      NOT NULL DEFAULT CURRENT_TIMESTAMP
                                            ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT pk_rooms           PRIMARY KEY (id),
    CONSTRAINT uq_rooms_number    UNIQUE (room_number)
);

-- ----------------------------------------------------------------------------
--  GUESTS
--  Persists guest identity independently from users so history is preserved
--  after the guest's stay ends. email is unique per guest profile.
-- ----------------------------------------------------------------------------
CREATE TABLE guests (
    id            INT          NOT NULL AUTO_INCREMENT,
    full_name     VARCHAR(150) NOT NULL,
    email         VARCHAR(100) NOT NULL,
    phone         VARCHAR(30)      NULL,
    document_id   VARCHAR(50)      NULL,   -- national ID or passport number
    created_at    TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at    TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP
                                          ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT pk_guests       PRIMARY KEY (id),
    CONSTRAINT uq_guest_email  UNIQUE (email)
);

-- ----------------------------------------------------------------------------
--  RESERVATIONS
--  Records every booking. staff_id captures which agent created the record.
--  nightly_rate is captured at booking time so future price changes to rooms
--  do not distort billing history. total_amount is derived at creation but
--  stored so queries do not need to recompute it.
--  Status lifecycle: confirmed → checked_in → checked_out (or cancelled).
--  When status moves to 'checked_out' the room status is updated to
--  'cleaning' and all connected staff are notified in real time via WebSocket.
-- ----------------------------------------------------------------------------
CREATE TABLE reservations (
    id              INT            NOT NULL AUTO_INCREMENT,
    room_id         INT            NOT NULL,
    guest_id        INT            NOT NULL,
    staff_id        INT            NOT NULL,
    check_in_date   DATE           NOT NULL,
    check_out_date  DATE           NOT NULL,
    nightly_rate    DECIMAL(8, 2)  NOT NULL,
    total_amount    DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    status          ENUM(
                      'confirmed',    -- booking created, awaiting arrival
                      'checked_in',   -- guest has arrived and room is occupied
                      'checked_out',  -- guest has departed, room needs cleaning
                      'cancelled'     -- reservation voided
                    )               NOT NULL DEFAULT 'confirmed',
    notes           TEXT                NULL,
    created_at      TIMESTAMP      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP      NOT NULL DEFAULT CURRENT_TIMESTAMP
                                               ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT pk_reservations       PRIMARY KEY (id),
    CONSTRAINT fk_res_room           FOREIGN KEY (room_id)
        REFERENCES rooms(id)  ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_res_guest          FOREIGN KEY (guest_id)
        REFERENCES guests(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_res_staff          FOREIGN KEY (staff_id)
        REFERENCES users(id)  ON DELETE RESTRICT ON UPDATE CASCADE
);

-- ----------------------------------------------------------------------------
--  NOTIFICATIONS
--  Persisted for every reservation-lifecycle event. When a guest checks out,
--  the backend immediately broadcasts a WebSocket message to ALL connected
--  staff dashboards so the room status update is visible without a refresh.
-- ----------------------------------------------------------------------------
CREATE TABLE notifications (
    id                   INT          NOT NULL AUTO_INCREMENT,
    user_id              INT          NOT NULL,
    title                VARCHAR(255) NOT NULL,
    message              TEXT         NOT NULL,
    type                 ENUM(
                           'reservation_created',   -- staff who created the booking
                           'guest_checked_in',       -- sent on check-in
                           'guest_checked_out',      -- sent on check-out (triggers broadcast)
                           'reservation_cancelled',  -- sent on cancellation
                           'general'
                         )            NOT NULL DEFAULT 'general',
    is_read              BOOLEAN      NOT NULL DEFAULT FALSE,
    related_reservation_id INT            NULL,   -- optional reference to the reservation
    created_at           TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_notifications           PRIMARY KEY (id),
    CONSTRAINT fk_notif_user              FOREIGN KEY (user_id)
        REFERENCES users(id)        ON DELETE CASCADE  ON UPDATE CASCADE,
    CONSTRAINT fk_notif_reservation       FOREIGN KEY (related_reservation_id)
        REFERENCES reservations(id) ON DELETE SET NULL ON UPDATE CASCADE
);

-- ----------------------------------------------------------------------------
--  INDEXES  — tuned for the most common application queries
-- ----------------------------------------------------------------------------

-- Fetch reservations created by a specific staff member (dashboard)
CREATE INDEX idx_res_staff          ON reservations (staff_id);

-- Filter reservations by current status (front-desk queue)
CREATE INDEX idx_res_status         ON reservations (status);

-- Availability search: find rooms by status and type
CREATE INDEX idx_rooms_status_type  ON rooms (status, room_type);

-- Fetch reservations for a specific room (history view)
CREATE INDEX idx_res_room           ON reservations (room_id);

-- Fetch reservations for a specific guest
CREATE INDEX idx_res_guest          ON reservations (guest_id);

-- Fetch unread notifications for a user (notification badge)
CREATE INDEX idx_notif_user_unread  ON notifications (user_id, is_read);

-- ============================================================================
