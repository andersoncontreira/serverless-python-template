CREATE TABLE IF NOT EXISTS store.categories (
    id INT NOT NULL AUTO_INCREMENT,
    uuid VARCHAR(60) NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    created_at timestamp NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp NULL,
    deleted_at timestamp NULL,
    active int(1) NULL DEFAULT 1,
    PRIMARY KEY (id)
)
